#!/usr/bin/env python
# encoding: utf-8

import sys
import cnoms
import watchdog
import time
from watchdog.observers import Observer
import requests

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
        print for_db

if __name__ == "__main__":
    local = "-l" in sys.argv
    app = cnoms.create_app(local)

    if "init" in sys.argv:
        init(app)
    elif "parse" in sys.argv:
        parse_single(sys.argv[2])
    elif "import" in sys.argv:
        from cnoms.server.server import import_website
        from cnoms.models import Entry
        Entry.create_table(fail_silently=True)
        import_website("localuser", sys.argv[2])
    elif "watch" in sys.argv:
        from cnoms.server.server import import_website
        from cnoms.utils import WatchChanges
        # start the file system observer
        event_handler = WatchChanges(sys.argv[2])
        observer = Observer()
        observer.schedule(event_handler, path=sys.argv[2], recursive=True)
        observer.start()

        # start the app and make the observer wait for it
        import cnoms.server.server
        app.run(host=app.config['HOST'], port=app.config['PORT'])

    else:
        import cnoms.server.server
        app.run(host=app.config['HOST'], port=app.config['PORT'])
