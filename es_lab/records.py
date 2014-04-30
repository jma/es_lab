# -*- coding: utf-8 -*-
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


def get_subfield(v, code):
    to_return = [d.get(code) for d in v.get("subfields") if d.get(code)]
    if len(to_return) == 1:
        to_return = to_return[0]
    return to_return




class Collection(list):
    def __init__(self, file_name):
        self.load(file_name)

    def load(self, file_name):
        import pymarc
        from es_config import marc2json
        for record in pymarc.parse_xml_to_array(file_name):
            fields = record.as_dict().get("fields")
            self.append(marc2json(fields))

    def to_json(self):
        import json
        return json.dumps(self, sort_keys=True, indent=4)


# third party modules
if __name__ == '__main__':
    usage = "usage: %prog [options]"

    from optparse import OptionParser

    parser = OptionParser(usage)

    parser.set_description("""
    """)

    (options, args) = parser.parse_args()
    col = Collection(file_name=args[0])
    print col.to_json()
