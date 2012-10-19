#!/usr/bin/env python
# encoding: utf-8

import sys
import cnoms

if __name__ == "__main__":
    local = "-l" in sys.argv
    app = cnoms.create_app(local)
    app.run(host=app.config['HOST'], port=app.config['PORT'])
