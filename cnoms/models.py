#!/usr/bin/env python
# encoding: utf-8
"""
    model for our database
"""

from . import db
from peewee import DateTimeField, TextField, CharField
from datetime import datetime

class Entry(db.Model):
    created = DateTimeField(default=datetime.now)
    user = CharField()
    site = CharField()
    fieldname = CharField()
    fieldtype = CharField()
    value = TextField()
    parent = CharField()
    speakr_hash = TextField()
    speakr_name = TextField()
    present_name = TextField()

    def __unicode__(self):
        return u"user: {} - site: {} ({} - {})".format(self.user, self.site,
                                                       self.fieldname,
                                                       self.value)
