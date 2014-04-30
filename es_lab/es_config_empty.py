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
    """ Transforme le marc en json

    Pour voir le Marc: ouvrir data/data.xml
    Pour la documentation des champs marc utilisés dans RERO DOC:
        http://www.rero.ch/pdfview.php?section=fiche&filename=metadonnees_rerodoc.pdf

    Exercice:
        rajouter les champs:
                language,
                cdu_class,
                keywords,
                document_type,
                institution

    Note: pour vusualiser le json:
        python es_lab/records.py data/data.xml
        ou
        http://localhost:5000/record/<recid>, par ex:
        http://localhost:5000/record/12739
    """
    from records import get_subfield
    to_return = {}

    for field in fields:
        for k, v in field.iteritems():
            if k == "001":
                to_return["recid"] = int(v)
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
            if k == "700":
                other_authors = get_subfield(v, "a")
                if other_authors:
                    to_return.setdefault("authors", {}).setdefault("other_authors", []).append(other_authors)
    return to_return


def get_facets_config():
    """ Définition des facettes

    Doc:
        http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html
    Exercice:
        remplir la config suivante pour toutes les facettes.
    """

    return {
        "aggs": {
            "institution": {
            },
            "facet_authors": {
            },
            "language": {
            },
            "cdu_class": {
            },
            "document_type": {
            },
            "keywords": {
            }
        }
    }


def get_hilights_config():
    """
    Doc:
        http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/search-request-highlighting.html#_postings_highlighter
    Exercice:
        rajouter la mise en évidence des termes trouvés pour:
            - title.title
            - title.subtitle
            - abstract
    Note: quand Elasticsearch trouve un champ avec des termes de recherche à
          mettre en évidence il remplace le texte d'origine. ! au paramètre
          "number_of_fragments".
    """

    return {
        "highlight": {
            "fields": {
            }
        }
    }


def get_analysis_config():
    """ Quelques analyzer custom.

    Ici sont pré-définis les analyzer dont vous aurez besoin dans le mapping.
    Ceux définits par défaut peuvent être vu ici:
    http://www.elasticsearch.org/guide/en/elasticsearch/guide/current/analysis-intro.html

    Doc:
    http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/analysis.html

    Exercice:
        lire est essayer de comprendre pourquoi on a définit des analyzers spécifiques.
    """
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
    """ Définit le mapping des champs json.

    Doc:
        http://www.elasticsearch.org/guide/en/elasticsearch/reference/current/mapping-core-types.html

    Exercice:
        tous les champs doivent être définis:
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
    Note pour tester un analyzer:
        1) aller dans sense (http://localhost:9200/_plugin/marvel/sense/index.html)
        2) GET heg/_analyze?analyzer=simple
          {
            "ma super phrase de test"
          }
    Tests:
        vous pouvez tester à tous moment en indexant les documents:
        python es_lab/es.py data/data.xml
    Astuce:
        il est important de bien définir le mapping en particulier pour les
        facettes, la recherche efficace dans du texte et le tris.
    """
    return {
            "language" : {
                "type": "string",
                "index": "not_analyzed"
            }
        }


def translate_facet_term(facet, term):
    """ Transforme les termes des facettes pour un joli affichage

    """
    from utils import cducode2str, langcode2str
    if facet == "cdu_class":
        return cducode2str(term)
    if facet == "language":
        return langcode2str(term)
    return term


def translate_facet_title(facet_title):
    """ Transforme le nom/titre des facettes pour un joli affichage

    """

    FACET_TITLE = {
        "cdu_class" : "Domains",
        "language" : "Language",
        "facet_authors" : "Author",
        "keywords" : "Keyword",
        "document_type" : "Document Type",
        "institution" : "Insitution"
    }
    return FACET_TITLE.get(facet_title, facet_title)
