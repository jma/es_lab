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


def marc2json(fields):
    from records import get_subfield
    to_return = {}

    for field in fields:
        for k, v in field.iteritems():
            if k == "001":
                to_return["recid"] = int(v)
            if k == "041":
                to_return["language"] = get_subfield(v, "a")
            if k == "080":
                cdu_class = get_subfield(v, "a")
                if cdu_class:
                    to_return["cdu_class"] = cdu_class
            if k == "100":
                to_return.setdefault("authors", {})["first_author"] = get_subfield(v, "a")
            if k == "245":
                to_return.setdefault("title", {})\
                         .setdefault("title", get_subfield(v, "a"))
                subtitle = get_subfield(v, "b")
                if subtitle:
                    to_return.setdefault("title", {})\
                             .setdefault("subtitle", get_subfield(v, "b"))
            if k == "520":
                abstract = get_subfield(v, "a")
                if abstract:
                    to_return["abstract"] = abstract
            if k == "695":
                keywords = get_subfield(v, "a")
                if keywords:
                    to_return["keywords"] = keywords
            if k == "700":
                other_authors = get_subfield(v, "a")
                if other_authors:
                    to_return.setdefault("authors", {}).setdefault("other_authors", []).append(other_authors)
            if k == "980":
                to_return["document_type"] = get_subfield(v, "a")
            if k == "980":
                to_return["institution"] = get_subfield(v, "b")
    return to_return


def get_facets_config():

    return {
        "aggs": {
            "institution": {
                "terms": {
                    "field": "institution",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            },
            "facet_authors": {
                "terms": {
                    "field": "facet_authors",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            },
            "language": {
                "terms": {
                    "field": "language",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            },
            "cdu_class": {
                "terms": {
                    "field": "cdu_class",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            },
            "document_type": {
                "terms": {
                    "field": "document_type",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            },
            "keywords": {
                "terms": {
                    "field": "keywords",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        }
    }


def get_highlights_config():
    return {
        "highlight": {
            "fields": {
                "abstract": {
                    "number_of_fragments": 0
                },
                "title.title": {
                    "number_of_fragments": 0
                },
                "title.subtitle": {
                    "number_of_fragments": 0
                }
            }
        }
    }


def get_analysis_config():
    return {
        "analysis" : {
            #-------- FILTER --------
            "filter" : {
                "filter_stop":{
                    "type":"stop",
                    #should be on server side in config directory
                    "stopwords_path" : "stop_words.txt",
                }
            },

            #-------- TOKENIZER --------
            "tokenizer" : {
                #rero stopwords has the form: keyword1; keyword2
                "custom_keywords" : {
                    "type" : "pattern",
                    "pattern" : "\s*;\s*|^\s+|\s+$",
                    "group" : "-1"
                }
            },

            #-------- ANALYZER --------
            "analyzer" : {
                "default": {
                    "type": "simple"
                    },
                #can make the same stop word list between all languages
                #multi-lingual as we can't detect query language,
                "french":{
                    "type":"french",
                    #should be on server side in config directory
                    "stopwords_path" : "stop_words.txt"
                },
                "english":{
                    "type":"english",
                    #"filter" : ["english", "filter_stop"]
                    "stopwords_path" : "stop_words.txt"
                    #should be on server side in config directory
                    #"stopwords_path" : "stop_words.txt"
                },
                "german":{
                    "type":"german",
                    #should be on server side in config directory
                    "stopwords_path" : "stop_words.txt"
                },
                "italian":{
                    "type":"italian",
                    #should be on server side in config directory
                    "stopwords_path" : "stop_words.txt"
                },
                "spanish":{
                    "type":"spanish",
                    #should be on server side in config directory
                    "stopwords_path" : "stop_words.txt"
                },
                "text" : {
                    "type": "combo",
                    #remove duplication, make index smaller
                    "deduplication": True,
                    #make the stopword useless as "la" is removed
                    #by "french" but added for all other languages
                    "sub_analyzers" : ["french", "english",
                        "spanish", "italian", "german" ]
                },
                "sort_title" : {
                        "tokenizer" : "keyword",
                        "filter" : ["standard", "asciifolding", "lowercase"]
                        },

                #keywords
                #rero stopwords has the form: keyword1; keyword2
                "custom_keywords": {
                    "type" : "custom",
                    "tokenizer" : "custom_keywords",
                    "filter" :  ["standard"]
                }
            }
        }
    }


def get_mapping_config():
    return {
            "recid" : {
                "type" : "integer"
            },
            "language" : {
                "type": "string",
                "index": "not_analyzed"
            },
            "cdu_class" : {
                "type": "string",
                "index": "not_analyzed"
            },
            "authors" : {
                "properties" : {
                    "first_author": {
                        "type": "string",
                        "fields" : {
                            "first_author": {
                                "copy_to" : ["facet_authors"],
                                "type": "string",
                                "analyzer": "simple"
                            }
                        }
                    },
                    "other_authors": {
                        "type": "string",
                        "fields" : {
                            "other_authors": {
                                "copy_to" : ["facet_authors"],
                                "type": "string",
                                "analyzer": "simple"
                            }
                        }
                    }
                }
            },
            "facet_authors" : {
                "type" : "string",
                "index": "not_analyzed"
            },
            "title" : {
                "properties" : {
                    "title": {
                        "copy_to" : ["sort_title"],
                        "type": "string",
                        "analyzer": "text"
                    },
                    "subtitle": {
                        "type": "string",
                        "analyzer": "text"
                    }
                }
            },
            "sort_title" : {
                "type" : "string",
                "analyzer": "sort_title"
            },
            "abstract" : {
                "type" : "string",
                "analyzer": "text"
            },
            "keywords" : {
                "type": "string",
                "analyzer": "custom_keywords"
            },
            "document_type" : {
                "type": "string",
                "index": "not_analyzed"
            },
            "institution" : {
                "type": "string",
                "index": "not_analyzed"
            }
        }


def translate_facet_term(facet, term):
    from utils import cducode2str, langcode2str
    if facet == "cdu_class":
        return cducode2str(term)
    if facet == "language":
        return langcode2str(term)
    return term


def translate_facet_title(facet_title):
    FACET_TITLE = {
        "cdu_class" : "Domains",
        "language" : "Language",
        "facet_authors" : "Author",
        "keywords" : "Keyword",
        "document_type" : "Document Type",
        "institution" : "Insitution"
    }
    return FACET_TITLE.get(facet_title, facet_title)
