#!/usr/bin/env python
# encoding: utf-8

import sys
import cnoms

def init(app):
    from cnoms import models
    models.Entry.create_table(fail_silently=True)
    test = models.Entry.create(
        user = "localuser",
        site = "tests",
        fieldname = "title",
        value = "Hello World!"
    )

def parse_single(filename):
    from cnoms.parser import parser
    with open(filename) as html:
        template, for_db = parser.parse_html(html.read())
        print template
        print for_db

if __name__ == "__main__":
    local = "-l" in sys.argv
    app = cnoms.create_app(local)

    if "init" in sys.argv:
        init(app)
    if "parse" in sys.argv:
        parse_single(sys.argv[2])
    if "import" in sys.argv:
        from cnoms.server.server import import_website
        from cnoms.models import Entry
        Entry.create_table(fail_silently=True)
        import_website('tests/test_website1', "dedan")

    else:
        import cnoms.server.server
        app.run(host=app.config['HOST'], port=app.config['PORT'])
