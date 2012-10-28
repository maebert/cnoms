#!/usr/bin/env python
# encoding: utf-8
"""
    parse what we get from the user
"""

import os
from cnoms import app
from cnoms.models import Entry
from bs4 import BeautifulSoup
import re

class Parser:
    rules = []
    resources = []
    tmp = {}
    _comp = {
        '__lt': lambda a, b: a < b,
        '__lte': lambda a, b: a <= b,
        '__gt': lambda a, b: a > b,
        '__gte': lambda a, b: a >= b,
        '__eq': lambda a, b: a == b,
        '__ne': lambda a, b: a != b,
        '__in': lambda a, b: a in b,
        '__nin': lambda a, b: a not in b,
        '__startswith': lambda a, b: a.startswith(b),
        '__endswith': lambda a, b: a.endswith(b),
    }
    fields = []


    def __init__(self, user, sitename, page=None):
        self.user = user
        self.sitename = sitename
        self.page = page

    @classmethod
    def rule(cls, **cond):
        def decorator(fn):
            cls.rules.append((cond, fn))
            return fn
        return decorator

    def _attr(self, node, attr, default=None):
        """Gets the value of a data attribute of a node"""
        attr = attr.replace("data_", "data-")
        if hasattr(node, "attrs"):
            return node.attrs.get(attr, default)

    def _add_data(self, node, key, value):
        if "data-"+key not in node.attrs:
            node.attrs["data-"+key] = value

    def evaluate(self, node, conds):
        attribute = lambda attr: self._attr(node, attr, None)
        for cond, value in conds.items():
            passes = True
            compared = False

            # Step 1: Are we matching a tag name?
            if cond == "tag":
                if not hasattr(node, "name"):
                    return False
                attribute = lambda attr: node.name

            # Step 2: Fancy comparators on node attributes (e.g. data_fieldname__in)
            if not compared and passes:
                for comp in self._comp:
                    if cond.endswith(comp):
                        compared = True
                        attr = cond.strip(comp)
                        passes = self._comp[comp](attribute(attr), value)

            # Step 3: Simple comparators on node attributes
            if not compared and passes:
                if value == True:
                    passes = attribute(cond)
                elif value == False:
                    passes = not attribute(cond)
                else:
                    passes = attribute(cond) == value
            if not passes:
                return False
        return True

    def parse(self, node, **kwargs):
        cont = True
        for cond, fn in self.rules:
            applies = self.evaluate(node, cond)
            if applies:
                any_applied = True
                result = fn(self, node, **kwargs)
                cont = min(cont, result)
        if cont:
            self.parse_children(node, **kwargs)
        return node

    def parse_children(self, node, **kwargs):
        if hasattr(node, 'children'):
            for child in node.children:
                    self.parse(child, **kwargs)

def parse_html(html_doc, user, sitename):
    """ return the template and a list of dictionaries with the
        containing all information we have to add to the database
    """
    import rules
    soup = BeautifulSoup(html_doc)
    parser = Parser(user, sitename)
    template = parser.parse(soup)
    print template.prettify(formatter=None)
    return template.prettify(formatter=None), parser.fields


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '..', '..', 'tests', 'test1.html')) as f:
        template, for_db = parse_html(f.read())
