#!/usr/bin/env python
# encoding: utf-8
import os, shutil
from cnoms import app
from cnoms.models import Entry
from parser import Parser
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
    sitename = os.path.basename(os.path.normpath(path_to_site))
    static_path = os.path.join(app.config['STATIC_MEDIA'], user, sitename)
    if not os.path.exists(static_path):
        os.makedirs(static_path)

    # copy static files
    # path = os.path.dirname(__file__)
    # new_static_path = os.path.join(path, '..', 'static', user, sitename)
    # if os.path.exists(new_static_path):
    #     shutil.rmtree(new_static_path)
    # if os.path.exists(os.path.join(path_to_site, 'static')):
    #     shutil.copytree(os.path.join(path_to_site, 'static'), new_static_path)
    # else:
    #     os.makedirs(os.path.join(new_static_path, 'static'))

    # if os.path.exists(os.path.join(path_to_site, '__icon.png')):
    #     shutil.copyfile(os.path.join(path_to_site, '__icon.png'), os.path.join(new_static_path, '__icon.png'))

    # create templates and add parsed stuff to db
    new_templates_path = os.path.join(app.config['TEMPLATE_PATH'], user, sitename)
    if not os.path.exists(new_templates_path):
        os.makedirs(new_templates_path)

    parser = Parser(user, sitename)
    for filename in os.listdir(path_to_site):
        if any([filename.endswith(ext) for ext in app.config['HTML_EXT']]):
            template = parser.parse_html(os.path.join(path_to_site, filename))
            save_path = os.path.join(new_templates_path, os.path.basename(filename))
            with open(save_path, 'w') as f:
                f.write(str(template))

    for entry in parser.fields:
        #print u"{:15}: {:40} ({})".format(entry.get("fieldname", "---"), entry.get("value", "---").strip("\n")[:40], entry.get("type", "/"))
        Entry.get_or_create(user=user, site=sitename, **entry)

    for resource in set(parser.resources):
        if any([resource.endswith(ext) for ext in app.config["STYLESHEET_EXT"]]):
            parser.parse_css(path_to_site, resource)

    for resource in set(parser.resources):
        source = os.path.join(path_to_site, resource)
        destination = os.path.join(static_path, resource)
        if not os.path.exists(source):
            print "WARNING", source, "does not exist."
        else:
            if not os.path.exists(os.path.dirname(destination)):
                os.makedirs(os.path.dirname(destination))
            shutil.copyfile(source, destination)
            print "Copying", resource
        
        #shutil.copyfile(os.path.join(path_to_site, '__icon.png'), os.path.join(new_static_path, '__icon.png'))
    return ''
