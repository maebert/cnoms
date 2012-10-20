#!/usr/bin/env python
# encoding: utf-8
"""
    parse what we get from the user
"""

import sys, os
from cnoms import app
from cnoms.models import Entry
from flask import request
from bs4 import BeautifulSoup
import re
import shutil

def data(node, attr, default=None):
    """Gets the value of a data attribute of a node"""
    if hasattr(node, "attrs"):
        return node.attrs.get("data-"+attr, default)

def add_data(node, key, value):
    if "data-"+key not in node.attrs:
        node.attrs["data-"+key] = value

def parse_collection(node, user, sitename, parent=None):
    collection = node.attrs['data-fieldname']
    fields = [{"fieldname": collection, 'type': "collection", "parent": parent}]
    item_template = None
    item_index = 1
    for child in node:
        if data(child, "type") == "item":
            if not item_template:
                item_template = child
            item_name = child.attrs.get('data-fieldname', "{}_{}".format(collection, item_index))
            add_data(child, "parent", collection)
            add_data(child, "fieldname", "{{ item.fieldname }}")
            fields.append({
                "fieldname": item_name,
                "parent": collection,
                "type": "item"
            })
            item_child, field = parse_node(child, user, sitename, parent=item_name)
            fields.extend(field)
            item_index += 1
    node.parsed = True
    node.clear()

    node.insert(0, "{% for item in "+collection+" %}")
    node.insert(1, item_template)
    node.insert(2, "{% endfor %}")
    return fields

def reroute_static(node, user, sitename):
    if 'src' in node.attrs and node['src'].startswith('static'):
        without_static = os.path.sep.join(node['src'].split(os.path.sep)[1:])
        filename = os.path.join(user, sitename, without_static)
        node['src'] = "{{ url_for('static', filename='%s') }}" % filename
    elif 'href' in node.attrs and node['href'].startswith('static'):
        without_static = os.path.sep.join(node['href'].split(os.path.sep)[1:])
        filename = os.path.join(user, sitename, without_static)
        node['href'] = "{{ url_for('static', filename='%s') }}" % filename


def parse_simple(node, user, sitename, parent=None):
    if not node.is_parsed:
        field = {'fieldname': node.attrs['data-fieldname'],
           'type': node.attrs.get('data-type', 'html'),
           'value': node.get_text(),
           'parent': parent}
        node.clear()
        parent_string = "item." if parent else ""
        node.insert(0, '{{ ' + parent_string + node.attrs['data-fieldname'] + ' }}')
        if parent:
            add_data(node, "parent", "{{ item.parent }}")
        node.is_parsed = True
        return [field]
    else:
        return []

def parse_node(head, user, sitename, parent=None):
    fields = []
    for node in head.find_all(True):
        if data(node, "fieldname"):
            if data(node, "type") == "collection":
                f = parse_collection(node, user, sitename, parent)
            elif data(node, "type") != "item": # Simple field
                f = parse_simple(node, user, sitename, parent)
            fields.extend(f)
        reroute_static(node, user, sitename)
    return head, fields

def insert_edit_fields(html):
    body = html.find("body")
    body.insert(-1, "{% if cnoms_edit %}{% include '/edit.jinja' %}{% else %}{% include '/edit_link.jinja' %}{% endif %}")

def parse_html(html_doc, user, sitename):
    """ return the template and a list of dictionaries with the
        containing all information we have to add to the database
    """
    soup = BeautifulSoup(html_doc)
    template, fields = parse_node(soup, user, sitename)
    insert_edit_fields(template)
    print template
    return template.prettify(formatter=None), fields

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


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '..', '..', 'tests', 'test1.html')) as f:
        template, for_db = parse_html(f.read())
