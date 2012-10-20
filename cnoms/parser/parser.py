#!/usr/bin/env python
# encoding: utf-8
"""
    parse what we get from the user
"""

import sys, os
from bs4 import BeautifulSoup
import re

def data(node, attr, default=None):
    """Gets the value of a data attribute of a node"""
    if hasattr(node, "attrs"):
        return node.attrs.get("data-"+attr, default)

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
        node.insert(0, '{{ ' + node.attrs['data-fieldname'] + ' }}')
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
            else: # Simple field
                f = parse_simple(node, user, sitename, parent)
            fields.extend(f)
        reroute_static(node, user, sitename)
    return head, fields

def insert_edit_fields(html):
    body = html.find("body")
    body.insert(-1, "{% if cnoms_edit %}{% include '/edit.jinja' %}{% endif %}")

def parse_html(html_doc, user, sitename):
    """ return the template and a list of dictionaries with the
        containing all information we have to add to the database
    """
    soup = BeautifulSoup(html_doc)
    template, fields = parse_node(soup, user, sitename)
    insert_edit_fields(template)
    print template
    return template, fields

if __name__ == '__main__':
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '..', '..', 'tests', 'test1.html')) as f:
        template, for_db = parse_html(f.read())
