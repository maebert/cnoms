#!/usr/bin/env python
# encoding: utf-8
import os, shutil
from cnoms import app
from cnoms.models import Entry
from parser import parse_html
from flask import request

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
    if os.path.exists(new_static_path):
        shutil.rmtree(new_static_path)
    if os.path.exists(os.path.join(path_to_site, 'static')):
        shutil.copytree(os.path.join(path_to_site, 'static'), new_static_path)
    else:
        os.makedirs(os.path.join(new_static_path, 'static'))
    if os.path.exists(os.path.join(path_to_site, '__icon.png')):
        shutil.copyfile(os.path.join(path_to_site, '__icon.png'), os.path.join(new_static_path, '__icon.png'))

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
    import json
    print json.dumps(db_fields, indent=2)
    for db_entry in db_fields:
        Entry.get_or_create(user=user, site=sitename, **db_entry)
    return ''
