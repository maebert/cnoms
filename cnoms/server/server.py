#!/usr/bin/env python
# encoding: utf-8
"""
    the actual flask app
"""
import os, glob
from cnoms.models import Entry
from cnoms.parser.parser import parse_html
from cnoms import app
from flask import Response, render_template_string, request
from datetime import datetime
import shutil

@app.route('/<user>/<site>/change_entry', methods=['POST'])
def change_entry(user, site):
    """receive entry changes via ajax call"""
    Entry.create(user=user, site=site, **request.form)
    return ''


@app.route('/<user>/<site>/<template>')
def show_template(user, site, template, edit=False):
    """render a template with the latest content for an entry"""

    entries = Entry.select().where(Entry.user==user, Entry.site==site).order_by(Entry.created.asc())
    latest_entries = []
    seen_entries = []
    for e in entries:
        if e.unique_id not in seen_entries:
            latest_entries.append(e)
            seen_entries.append(e.unique_id)
    templates_path = app.jinja_loader.searchpath[0]
    template_string = open(os.path.join(templates_path, user, site, template)).read()
    data = {entry.fieldname: entry.value for entry in latest_entries}
    return render_template_string(template_string, __user=user, __site=site, cnoms_edit=edit, **data)

@app.route('/<user>/<site>/<template>/edit')
def edit_page(user, site, template):
    return show_template(user, site, template, edit=True)

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
    shutil.rmtree(os.path.join(path, '..', 'static', user))
    if os.path.exists(os.path.join(path_to_site, 'static')):
        shutil.copytree(os.path.join(path_to_site, 'static'),
                        new_static_path)

    # create templates and add parsed stuff to db
    new_templates_path = os.path.join(path, '..', 'templates', user, sitename)
    if not os.path.exists(new_templates_path):
        os.makedirs(new_templates_path)
    print os.path.join(path_to_site, '*.html')

    db_fields = []
    for filename in os.listdir(path_to_site):
        if any([filename.endswith(ext) for ext in app.config['HTML_EXT']]):
            template, for_db = parse_html(open(os.path.join(path_to_site, filename)).read(), user, sitename)
            db_fields.extend(for_db)
            save_path = os.path.join(new_templates_path, os.path.basename(filename))
            with open(save_path, 'w') as f:
                f.write(str(template))
    print db_fields
    for db_entry in db_fields:
        count = Entry.select().where(Entry.user==user,
                                     Entry.site==sitename,
                                     Entry.type==db_entry['type'],
                                     Entry.value==db_entry['value'],
                                     Entry.fieldname==db_entry['fieldname']).count()
        if count == 0:
            Entry.create(user=user, site=sitename, **db_entry)

