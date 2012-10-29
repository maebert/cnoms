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
    css_url = re.compile("[^\(]*url[\s]*\([\s]*([^\)]*)[\s]*\)[^\)]*")
    css_import = re.compile("@import[\s]+(url)?[\s]*\(?([^\);]*)")

    def __init__(self, user, sitename):
        self.user = user
        self.sitename = sitename

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

    def parse_html(self, filename):
        import rules
        with open(filename) as htmlfile:
            soup = BeautifulSoup(htmlfile.read())
            template = self.parse(soup)
            return template.prettify(formatter=None)

    def parse_css(self, site_path, filename):
        """Parses a CSS, LESS or SASS file, recursively parsing all files declared
        via @import commands and adding all url(...) objects to the resources."""
        with open(os.path.join(site_path, filename)) as cssfile:
            for line in cssfile.readlines():
                m = self.css_url.match(line.strip())
                if m:
                    resource = m.group(1).strip('"').strip("'")
                    path_to_resource = os.path.join(os.path.dirname(filename), resource)
                    self.resources.append(path_to_resource)
                imp = self.css_import.match(line);
                if imp:
                    resource = imp.group(2).strip('"').strip("'")
                    if not any([resource.endswith(ext) for ext in app.config["STYLESHEET_EXT"]]):
                        resource += os.path.splitext(filename)[1]
                    path_to_resource = os.path.join(os.path.dirname(filename), resource)
                    self.resources.append(path_to_resource)
                    self.parse_css(site_path, path_to_resource)
