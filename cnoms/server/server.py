#!/usr/bin/env python
# encoding: utf-8
"""
    the actual flask app
"""
import os, glob
from cnoms.models import Entry
from cnoms.parser.parser import parse_html
from cnoms import app
from flask import Response, render_template_string
from datetime import datetime
import shutil


@app.route('/<user>/<site>/<template>')
def show_template(user, site, template):
    """render a template with the latest content for an entry"""
    entries = Entry.select().where(Entry.user==user, Entry.site==site).execute()
    # entries = Entry.select().where(Entry.user==user, Entry.site==site).order_by(('created', 'desc')).execute()
    entries = [e for e in entries]
    latest_entries = []
    seen_entries = []
    for e in entries:
        if e.unique_id not in seen_entries:
            latest_entries.append(e)
            seen_entries.append(e.unique_id)
    templates_path = app.jinja_loader.searchpath[0]
    template_string = open(os.path.join(templates_path, user, site, template)).read()
    return render_template_string(template_string, entries=entries)

def import_website(path_to_site, user):
    """import a website

        * create templates
        * add content to database
        * copy static files
    """
    # copy static files
    path = os.path.dirname(__file__)
    sitename = os.path.basename(os.path.normpath(path_to_site))
    new_static_path = os.path.join(path, '..', 'static', user, sitename)
    # # for testign
    # shutil.rmtree(new_static_path)
    # shutil.rmtree(os.path.join(path, '..', 'static', user))
    # shutil.rmtree(os.path.join(path, '..', 'templates', user))
    if os.path.exists(os.path.join(path_to_site, 'static')):
        shutil.copytree(os.path.join(path_to_site, 'static'),
                        new_static_path)

    # create templates and add parsed stuff to db
    new_templates_path = os.path.join(path, '..', 'templates', user, sitename)
    if not os.path.exists(new_templates_path):
        os.makedirs(new_templates_path)
    for html_file in glob.glob(os.path.join(path_to_site, '*.html')):
        template, for_db = parse_html(open(html_file).read(), user, sitename)
        save_path = os.path.join(new_templates_path, os.path.basename(html_file))
        with open(save_path, 'w') as f:
            f.write(str(template))

        for db_entry in for_db:
            Entry.create(user=user,
                         site=sitename,
                         fieldname=db_entry['fieldname'],
                         fieldtype=db_entry['type'],
                         value=db_entry['value'],
                         parent=db_entry.get('parent', None))

