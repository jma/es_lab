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

from flask import Flask,  render_template, current_app, request, jsonify
from flask.ext.assets import Environment, Bundle


def create_app():
    app = Flask(__name__, static_url_path='')
    app.secret_key = '8943oqfjkdas9324'

    # Tell flask-assets where to look for our coffeescript and sass files.
    assets = Environment(app)
    #minify css and js
    app.config['ASSETS_DEBUG'] = True
    #app.config['ELASTICSEARCH_URL'] = "http://doc.test.rero.ch:9200"

    js = Bundle('bower_components/jquery/dist/jquery.js',
                filters='jsmin',
                output='gen/js/es_lab_jquery-1.0.js')
    assets.register('js_jquery', js)
    js = Bundle('bower_components/bootstrap/dist/js/bootstrap.js',
                filters='jsmin',
                output='gen/js/es_lab-1.0.js')
    assets.register('js_all', js)
    css = Bundle('css/es_lab.css',
                 'bower_components/bootstrap/dist/css/bootstrap.css',
                 filters='cssmin',
                 output='gen/css/es_lab-1.0.css')
    assets.register('css_all', css)
    app.jinja_env.add_extension('jinja2.ext.do')
    from es_config import translate_facet_title, translate_facet_term

    app.jinja_env.globals.update(translate_facet_title=translate_facet_title)
    app.jinja_env.globals.update(translate_facet_term=translate_facet_term)
    #assets.debug = True
    from es import setup_app
    setup_app(app)

    @app.route('/')
    def search():
        user_query = request.args.get("p")

        rg = request.args.get("rg", 10)
        rg = int(rg)

        jrec = request.args.get("jrec", 0)
        jrec = int(jrec)

        so = request.args.get("so", "d")
        sf = request.args.get("sf", "")

        facet_filters = []
        for ff in request.args.getlist("facet_filter"):
            facet_filters.append((ff.split(":")))
        print facet_filters
        es = current_app.extensions.get("elasticsearch")
        results = es.search(user_query=user_query,
                            rg=rg, sf=sf, so=so, jrec=jrec,
                            facet_filters=facet_filters)
        hidden_fields = {
            "so": so,
            "sf": sf
        }
        p = user_query or ""
        return render_template("index.html",
                               results=results,
                               hidden_fields=hidden_fields,
                               p=p,
                               facet_filters=facet_filters)


    @app.route('/record/<recid>')
    def get_record(recid):
        es = current_app.extensions.get("elasticsearch")
        res = es.get_record(int(recid))
        return jsonify(res)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html', title=u"Page not found", msg=u"What you are searching is not here."), 404
    return app
