#!/usr/bin/env python
# encoding: utf-8
"""
    the actual flask app
"""
import os, glob, json
import os, glob
from flask import Response
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

@app.route('/data/<user>/<site>')
@app.route('/data/<user>/<site>/<fieldname>')
def get_field_history(user, site, fieldname=None):
    """get the history of one field (for the history slider) (or for all - global slider)"""
    if fieldname:
        entries = Entry.select().where(Entry.user==user,
                                       Entry.site==site,
                                       Entry.fieldname==fieldname).order_by(Entry.created.desc())
    else:
        entries = Entry.select().where(Entry.user==user,
                                       Entry.site==site).order_by(Entry.created.desc())
    data = [{entry.fieldname: entry.value} for entry in entries]
    return json.dumps(data)

@app.route('/<user>/<site>')
@app.route('/<user>/<site>/<template>')
def show_template(user, site, template=None, edit=False):
    """render a template with the latest content for an entry"""
    entries = Entry.select().where(Entry.user==user, Entry.site==site).order_by(Entry.created.asc())
    seen_entries = []
    simple_entries = []
    collections = {}
    items = {}
    for e in entries:
        if e.unique_id not in seen_entries:
            if e.type == "collection":
                collections[e.fieldname] = []
            elif e.type == "item":
                collections.get(e.parent, {}).append(e.fieldname)
                items[e.fieldname] = {}
            elif e.parent:
                items.get(e.parent, {})[e.fieldname] = e.value
            else:
                simple_entries.append(e)
            seen_entries.append(e.unique_id)

    data = {entry.fieldname: entry.value for entry in simple_entries}
    collections = {k: [items.get(item, {}) for item in kitems] for k, kitems in collections.items()}
    data.update(collections)

    templates_path = app.jinja_loader.searchpath[0]
    if not template:
        template = 'index.html'
    current_template_path = os.path.join(templates_path, user, site, template)
    if not os.path.exists(current_template_path):
        return Response(status_code=404)
    template_string = open(current_template_path).read()
    return render_template_string(template_string, __user=user, __site=site, cnoms_edit=edit, **data)

@app.route('/<user>/<site>/<template>/edit')
def edit_page(user, site, template):
    return show_template(user, site, template, edit=True)

# TODO: restrict this function to work only localy
@app.route('/import_website', methods=['POST'])
def import_website(user=None, path_to_site=None):
    """import a website

        * create templates
        * add content to database
        * copy static files
    """
    print 'import_website'
    if not (user and path_to_site):
        path_to_site = request.args['path_to_site']
        user = request.args['user']
    # copy static files
    path = os.path.dirname(__file__)
    sitename = os.path.basename(os.path.normpath(path_to_site))
    new_static_path = os.path.join(path, '..', 'static', user, sitename)
    if os.path.exists(os.path.join(path, '..', 'static', user)):
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
        Entry.get_or_create(user=user, site=sitename, **db_entry)
    return ''
