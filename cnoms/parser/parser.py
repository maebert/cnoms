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

def parse_collection(node, parent=None):
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
            item_child, field = parse_node(child, parent=item_name)
            fields.extend(field)
            item_index += 1
    node.parsed = True
    node.clear()

    node.insert(0, "{% for item in "+collection+" %}")
    node.insert(1, item_template)
    node.insert(2, "{% endfor %}")
    return fields

def parse_simple(node, parent=None):
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

def parse_node(head, parent=None):
    fields = []
    for node in head.find_all(True):
        if data(node, "fieldname"):
            if data(node, "type") == "collection":
                f = parse_collection(node, parent)
            else: # Simple field
                f = parse_simple(node, parent)
            fields.extend(f)
    return head, fields 

def parse_html(html_doc):
    """ return the template and a list of dictionaries with the
        containing all information we have to add to the database
    """
    soup = BeautifulSoup(html_doc)
    return parse_node(soup)


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '..', '..', 'tests', 'test1.html')) as f:
        template, for_db = parse_html(f.read())
