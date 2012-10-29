#!/usr/bin/env python
# encoding: utf-8

class Base:
    DEBUG = True
    SECRET_KEY = 'seenomess'
    DEBUG = True
    DATABASE = {
        'name': 'cnoms.db',
        'engine': 'peewee.SqliteDatabase',
    }
    HOST = '0.0.0.0'
    PORT = 5000
    HTML_EXT = (".htm", ".html")
    STATIC_EXT = (".css", ".less", ".scss", ".sass", ".js", ".png", ".jpeg", ".jpg", ".gif", ".ico", ".svg")
    STYLESHEET_EXT = (".css", ".less", ".scss", ".sass")
    STATIC_MEDIA = "cnoms/static/"
    TEMPLATE_PATH = "templates/"

class Local(Base):
    HOST = 'localhost'
