#!/usr/bin/env python
# encoding: utf-8
"""
    the actual flask app
"""
import os, glob, json
from flask import Response
from cnoms.models import Entry
from cnoms.parser.parser import parse_html
from cnoms import app
from flask import Response, render_template_string, request, render_template
from datetime import datetime
from collections import defaultdict

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route('/<user>/<site>/__admin')
def show_site_admin(user, site):
    """admin view for a site"""

    # get all templates
    templates_path = app.jinja_loader.searchpath[0]
    templates = glob.glob(os.path.join(templates_path, user, site, '*.html'))
    templates = [os.path.basename(t) for t in templates]

    # get all fieldnames
    fields = []
    entries = Entry.select().where(Entry.user==user, Entry.site==site).order_by(Entry.created.desc())
    for entry in entries:
        d = {'type': entry.type, 'fieldname': entry.fieldname, 'value': entry.value}
        if not d in fields:
            fields.append(d)
    return json.dumps({"templates": templates, "fields": fields})

#/<username>: For each site of the user: Name, Preview image. HTML: each site links to following:
@app.route('/<user>')
def show_user(user):
    """show all information for a user"""
    leads = Entry.select().where(Entry.user==user).group_by(Entry.site)
    sites = []
    for site in leads:
        sites.append({
            "name": site.site
        })
    return render_template('show_user.html', sites=sites, user=user)


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
                collections.get(e.parent, []).append(e.fieldname)
                items[e.fieldname] = {"__parent": e.parent, "__name": e.fieldname}
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
        return 'Response(status_code=404)', 404
    template_string = open(current_template_path).read()
    return render_template_string(template_string, __user=user, __site=site, cnoms_edit=edit, **data)

@app.route('/<user>/<site>/<template>/edit')
def edit_page(user, site, template):
    return show_template(user, site, template, edit=True)

