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


def langcode2str(lang):
    import pycountry
    try:
        lang_name = pycountry.languages.get(bibliographic=lang).name
    except:
        return lang
    return lang_name


CDUCODE2STR = {
    "52": "Astronomy, Astrophysics",
    "524.8": "Cosmology",
    "57/59": "Biology, Life sciences",
    "57": "Biology",
    "60": "Biotechnology",
    "58": "Botany",
    "59": "Zoology",
    "54": "Chemistry",
    "543": "Analytical chemistry",
    "548": "Crystallography",
    "549": "Mineralogy",
    "574": "Ecology",
    "51": "Mathematics",
    "519.2": "Probabilites, Statistics",
    "53": "Physics",
    "55/56": "Earth sciences",
    "55": "Geology",
    "551": "Climate",
    "556": "Hydrology",
    "56": "Paleontology",
    "35": "Public administration",
    "39": "Anthropology, Ethnology",
    "72": "Architecture",
    "71": "Urbanism",
    "7": "Arts",
    "73/77": "Visual arts",
    "75": "Painting",
    "77": "Photography",
    "7.071": "Art history",
    "78": "Music",
    "34": "Law",
    "33": "Economics",
    "37": "Education",
    "376": "Special education",
    "370": "Orthophony",
    "91": "Geography",
    "93/94": "History",
    "902": "Archeology",
    "929.5": "Genealogy",
    "931": "Ancient history",
    "94": "Medieval and modern history",
    "903": "Pre-history",
    "81": "Language, Linguistics",
    "81Â´28": "Dialectology",
    "82": "Literature",
    "1": "Philosophy",
    "16": "Logic",
    "159.9": "Psychology",
    "2": "Religion, Theology",
    "294/299": "Orientalism",
    "65": "Information, communication and media sciences",
    "02": "Library sciences",
    "32": "Political sciences",
    "796": "Sports sciences",
    "3": "Social sciences",
    "31": "Demography, Sociology, Statistics",
    "36": "Social work",
    "004": "Computer science",
    "61": "Medicine",
    "616": "Clinical medicine",
    "616.31": "Dental medicine",
    "616-083": "Nursing",
    "61": "Health",
    "613.2": "Nutrition and Dietetics",
    "614.253.5": "Midwife",
    "615": "Therapeutic. Pharmacy, Pharmacology",
    "615.8": "Physiotherapy",
    "615.84": "Medical Radiation Technology",
    "6": "Engineering",
    "63": "Agriculture, Agronomy",
    "66": "Chemical technology",
    "664": "Food production and preservation",
    "663": "Beverage industry",
    "621.3": "Electricity",
    "621.38": "Electronics",
    "620.9": "Energy",
    "621": "Industrial Engineering",
    "620.1": "Materials",
    "621.01": "Mechanics",
    "621.762": "Powder metallurgy",
    "681": "Microengineering",
    "621.39": "Telecommunications"
}


def cducode2str(code):
    return CDUCODE2STR.get(code, code)
