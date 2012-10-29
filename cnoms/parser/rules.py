#!/usr/bin/env python
# encoding: utf-8
"""
Extensible rule system for parsing. Each rule must register itself using the
Parser's `rule` decorator. The arguments specify to which node type the rule
applies. The rules are checked against the attributes of that node. E.g.

    @Parser.rule(data_type="image", src="logo.png")

will match `<div data-fieldname="start-img" data-type="image" src="logo.png">`
Apart from matching a specific value, @Parser.rule(data_type=True) will match
any node in which the `data-type` attribute is present, and conversely
@Parser.rule(data_type=False) all nodes that do not have `data-type` in their
attributes. More complex filters can be constructed using the operators
__lt, __lte, __gt, __gte, and __ne, checking whether the attribute is <, <=,
>, >= or != the given argument, and __in and __nin, checking whether the 
attribute is in the given iterable, and __startswith and __endswith as well as
__not_startswith and __not_endswith.
Furthermore the `tag` parameters checks against the node's tag name. Hence

    @Parser.rule(tag__in=('ul', 'ol'), data_fieldname=True, data_type__ne="item")

will match all `ul` or `ol` tags that have a `data-fieldname` specified, and
have a `data_type` specified, but its' value is not "item". Using several
decorators can be helpful, as well:

    @Parser.rule(src__not_startswith="static")
    @Parser.rule(src=False)
    def no_static_link(parser, node, **kwargs):
        ....

will apply the method no_static_link to all nodes that have a `src` attribute
that does not start with "static" or have no `src` attribute at all.

The Parser itself will recursively traverse the HTML's DOM structure and apply
all matching rules for each node. If a any rule that applies to the current
node returns False, its children will not be parsed. This can be useful if you
want to parse a node's children with special arguments, ie. by calling

    parser.parse_children(node, parent="blog")

at the end of your rule. Otherwise your rule must return True. The first 
argument of a rule will always be a Parser instance, the second the node to be
parsed. Any number of keyword arguments may follow. A minimal rule will have
have this format:

    @Parser.rule()
    def identity(parser, node, **kwargs):
        return True

The body of the rule may manipulate the node and extend the parsers' fields
and resources.
"""
from cnoms import app
from parser import Parser
import os
import random

@Parser.rule(data_type="item")
def parse_item(parser, node, parent=None, template="", **kwargs):
    name = node.attrs.get('data-fieldname', "{}_{}".format(parent, hex(random.randint(0,256**3))[2:])).replace("-", "_")
    parser._add_data(node, "parent", parent)
    parser._add_data(node, "fieldname", "{{ item.__name }}")
    field = {
        "fieldname": name,
        "parent": parent,
        "type": "item"
    }
    parser.fields.append(field)
    parser.parse_children(node, parent=name)
    if not parser.tmp.get(template, True):
        parser.tmp[template] = node
    return False

@Parser.rule(data_fieldname=True, data_type="collection")
def parse_collection(parser, node, parent=None, **kwargs):
    name = node.attrs['data-fieldname'].replace("-", "_")
    field = {"fieldname": name, 'type': "collection", "parent": parent}
    parser.fields.append(field)
    parser.tmp['item_template_'+name] = None
    parser.parse_children(node, parent=name, template='item_template_'+name)
    node.parsed = True
    node.clear()

    node.insert(0, "{% for item in "+name+" %}")
    node.insert(1, parser.tmp['item_template_'+name])
    node.insert(2, "{% endfor %}")

    return False

def rereoutse_field(parser, node, field):
    filename = node[field]
    if any(filename.endswith(ext) for ext in app.config['STATIC_EXT']):
        parser.resources.append(filename)
        new_filename = os.path.join(parser.user, parser.sitename, filename)
        node[field] = "{{ url_for('static', filename='%s') }}" % new_filename

@Parser.rule(src=True)
def reroute_static_src(parser, node, **kwargs):
    rereoutse_field(parser, node, "src")
    return True

@Parser.rule(href=True)
def reroute_static_href(parser, node, **kwargs):
    rereoutse_field(parser, node, "href")
    return True
 
@Parser.rule(data_fieldname=True, data_type__nin=("collection", "item"))
def parse_simple(parser, node, parent=None, **kwargs):
    name = node.attrs['data-fieldname'].replace("-", "_")
    value = u"".join([unicode(c) for c in node.contents])
    field = {'fieldname': name,
       'type': node.attrs.get('data-type', 'html'),
       'value': value,
       'parent': parent}
    parser.fields.append(field)
    node.clear()
    parent_string = "item." if parent else ""
    node.insert(0, '{{ ' + parent_string + name + ' }}')
    if parent:
        parser._add_data(node, "parent", "{{ item.__name }}")
    return True

@Parser.rule(tag="body")
def insert_edit_fields(parser, node, parent=None, **kwargs):
    node.insert(-1, "{% include '/edit_link.jinja' %}")
    return True
