#!/usr/bin/env python
# encoding: utf-8

import sys
import cnoms

def init(app):
    from cnoms import models
    models.Entry.create_table(fail_silently=True)

if __name__ == "__main__":
    local = "-l" in sys.argv
    app = cnoms.create_app(local)

    if "init" in sys.argv:
        init(app)
    else:
        app.run(host=app.config['HOST'], port=app.config['PORT'])
