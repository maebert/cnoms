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

    def unique_id():
        """this can be used to identify a certain entry (ignoring its value or date)"""
        return "{}_{}_{}_{}".format(self.user, self.site, self.fieldname, self.type)

    def __unicode__(self):
        return u"user: {} - site: {} ({} - {})".format(self.user, self.site,
                                                       self.fieldname,
                                                       self.value)
