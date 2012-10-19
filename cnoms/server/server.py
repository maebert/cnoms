#!/usr/bin/env python
# encoding: utf-8
"""
    the actual flask app
"""
import os
from cnoms.models import Entry
from cnoms import app
from flask import Response, render_template
from datetime import datetime

@app.route('/<user>/<site>/<template>')
def show_template(user, site, template):
    """render a template with the latest content for an entry"""
    entries = Entry.select().where(user=user,
                                   site=site).order_by(('created', 'desc')).execute()
    entries = [e for e in entries]
    latest_entries = []
    seen_entries = []
    for e in entries:
        if e.unique_id not in seen_entries:
            latest_entries.append(e)
            entries_ips.append(f.unique_id)
    templates_path = app.jinja_loader.searchpath[0]
    template_string = open(os.path.join(templates_path, template)).read()
    return render_template_string(template_string, entries)

