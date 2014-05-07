## -*- coding: utf-8 -*-
##
## This file is part of ES_lab.
## Copyright (C) 2014 RERO.
##
## ES_lab is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## ES_lab is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
elasticsearch wrapper
---------------------
"""
from werkzeug.utils import cached_property
from pyelasticsearch import ElasticSearch as PyElasticSearch


class ElasticSearch(object):
    """
    Flask extension
    """
    def __init__(self, app=None):
        self.app = app

        # TODO: to put in config?
        self.records_doc_type = "records"

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize a Flask application.

        Only one Registry per application is allowed.
        """
        app.config.setdefault('ELASTICSEARCH_URL', 'http://localhost:9200/')
        app.config.setdefault('ELASTICSEARCH_INDEX', "heg")
        app.config.setdefault('ELASTICSEARCH_NUMBER_OF_SHARDS', 1)
        app.config.setdefault('ELASTICSEARCH_NUMBER_OF_REPLICAS', 0)
        app.config.setdefault('ELASTICSEARCH_DATE_DETECTION', False)
        app.config.setdefault('ELASTICSEARCH_NUMERIC_DETECTION', False)
        from es_config import get_analysis_config
        app.config.setdefault('ELASTICSEARCH_ANALYSIS', get_analysis_config())

        # Follow the Flask guidelines on usage of app.extensions
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        if 'elasticsearch' in app.extensions:
            raise Exception("Flask application already initialized")

        app.extensions['elasticsearch'] = self
        self.app = app

    @cached_property
    def connection(self):
        return PyElasticSearch(self.app.config['ELASTICSEARCH_URL'])

    def create_index(self, index=None):
        """Create the given index.

        Also set basic configuration and doc type mappings.

        :param index: [string] index name

        :return: [bool] True if success
        """
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        if self.index_exists(index=index):
            return True
        #create index
        index_settings = {
            #should be set to 1 for exact facet count
            "number_of_shards":
            self.app.config['ELASTICSEARCH_NUMBER_OF_SHARDS'],

            #in case of primary shard failed
            "number_of_replicas":
            self.app.config['ELASTICSEARCH_NUMBER_OF_REPLICAS'],

            #disable automatic type detection
            #that can cause errors depending of the indexing order
            "date_detection":
            self.app.config['ELASTICSEARCH_DATE_DETECTION'],
            "numeric_detection":
            self.app.config['ELASTICSEARCH_NUMERIC_DETECTION']
        }
        if self.app.config['ELASTICSEARCH_ANALYSIS']:
            index_settings.update(self.app.config['ELASTICSEARCH_ANALYSIS'])
        self.connection.create_index(index=index, settings=index_settings)

        print "Index created"
        from es_config import get_mapping_config

        #mappings
        self._mapping(index=index, doc_type=self.records_doc_type,
                      fields_mapping=get_mapping_config())
        return True

    def delete_index(self, index=None):
        """Delete the given index.

        :param index: [string] index name

        :return: [bool] True if success
        """
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        try:
            self.connection.delete_index(index=index)
            return True
        except:
            return False

    def index(self, docs):
        if not docs:
            return []
        self.app.logger.info("Indexing: %d records for %s" % (len(docs),
                             self.records_doc_type))
        results = self.connection.bulk_index(index=self.app.config.get("ELASTICSEARCH_INDEX"),
                                             doc_type=self.records_doc_type, docs=docs,
                                             id_field='recid',
                                             refresh=self.app.config.get("DEBUG"))
        errors = []
        for it in results.get("items"):
            if it.get("index").get("error"):
                errors.append((it.get("index").get("_id"), it.get("index").get("error")))
        return errors

    def search(self, user_query=None, rg=10, sf=None, so="d", jrec=0, facet_filters=[]):
        """Perform a search query.

        Note: a lot of work to do.

        :param user_query: [string] search query
        :param rg: [int] number of results to return
        :param sf: [string] sort field
        :param so: [string] sort order in [d,a]
        :param jrec: [int] result offset for paging
        :param facet_filters: [list of tupple of strings] filters to prune the
        results. Each filter is defined as a tupple of term, value: (i.e.
        [("facet_authors", "Ellis, J.")])

        :return: [object] response
        """
        index = self.app.config['ELASTICSEARCH_INDEX']

        es_query = {}

        #search main options
        main_options = {
            "size": rg,
            "from": jrec,
            "fields": [
                "recid",
                "language",
                "cdu_class",
                "authors.first_author",
                "title.title",
                "title.subtitle",
                "abstract",
                "keywords",
                "authors.other_authors",
                "document_type",
                "institution"
            ]
        }
        es_query.update(main_options)

        query = {
            "query": {
                "match_all": {}
            }
        }

        if user_query:
            query["query"] = {
                "query_string": {
                    "fields" : ["title.title^4", "title.subtitle^2", "abstract"],
                    "query": user_query
                }
            }

        # facet_filters
        es_filters = []
        for term, value in facet_filters:
            es_filters.append({
                "term": {
                    term: value
                }
            })

        if facet_filters:
            es_query.update({
                "query": {
                    "filtered": {
                        "query": query.get("query"),
                        "filter": {
                            "bool": {
                                "must": es_filters
                            }
                        }
                    }
                }
            })
        else:
            es_query.update(query)

        # sorting
        sort_options = {}
        if sf:
            sort_options = {
                "sort": [{
                    "%s" % sf: {
                        "order": "desc" if so == "d" else "asc"
                        }
                }]
            }
        es_query.update(sort_options)

        # facet configuration
        from es_config import get_facets_config, get_highlights_config
        es_query.update(get_facets_config())

        # hightlight configuration
        es_query.update(get_highlights_config())

        results = self.process_results(self.connection.search(es_query,
                                       index=index,
                                       doc_type=self.records_doc_type))
        return results

    def _mapping(self, index, doc_type, fields_mapping, parent_type=None):
        mapping = {
            doc_type: {
                "properties": fields_mapping
            }
        }

        self.connection.put_mapping(index=index, doc_type=doc_type,
                                        mapping=mapping)
        return True

    def process_results(self, results):
        to_return = {
            "total": results.get("hits").get("total"),
            "hits": [],
            "facets": results.get("aggregations", {})
        }
        highlights = [r.get("highlight") for r in results.get("hits").get("hits")],
        for hit in results.get("hits").get("hits"):
            fields = hit.get("fields")
            fields.update(hit.get("highlight", {}))
            to_return["hits"].append(fields)
        return to_return

    def index_exists(self, index=None):
        """Check if the index exists in the cluster.

        :param index: [string] index name

        :return: [bool] True if exists
        """
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        if self.connection.status().get("indices").get(index):
            return True
        return False

    def get_record(self, recid, index=None):
        if index is None:
            index = self.app.config['ELASTICSEARCH_INDEX']
        return self.connection.get(index=index, doc_type=self.records_doc_type, id=recid)
def setup_app(app):
    ElasticSearch(app)


# import of standard modules
from optparse import OptionParser

# third party modules
if __name__ == '__main__':
    usage = "usage: %prog [options]"

    parser = OptionParser(usage)

    parser.set_description("""
    """)
    from records import Collection

    (options, args) = parser.parse_args()
    col = Collection(file_name=args[0])
    print "Indexing: %d records" % len(col)

    from flask import Flask, current_app

    app = Flask(__name__)
    with app.app_context():
        # within this block, current_app points to app.
        setup_app(current_app)
        es = current_app.extensions.get("elasticsearch")
        es.delete_index()
        es.create_index()
        es.index(col)
        es.connection.refresh("heg")
        es.search(user_query="abstract:commission")
