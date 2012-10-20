#!/usr/bin/env python
# encoding: utf-8
"""
    parse what we get from the user
"""

import sys, os
from bs4 import BeautifulSoup
import re

def parse_html(html_doc, user, sitename):
    """ return the template and a list of dictionaries with the
        containing all information we have to add to the database
    """
    for_db = []
    soup = BeautifulSoup(html_doc)
    for s in soup.find_all(True):
        if 'data-fieldname' in s.attrs:
            tmp = {'fieldname': s.attrs['data-fieldname'],
                   'type': s.attrs.get('data-type', 'html'),
                   'value': s.get_text()}
            for_db.append(tmp)
            s.clear()
            s.insert(0, '{{ ' + s.attrs['data-fieldname'] + ' }}')
        if 'src' in s.attrs and s['src'].startswith('static'):
            without_static = os.path.sep.join(s['src'].split(os.path.sep)[1:])
            filename = os.path.join(user, sitename, without_static)
            s['src'] = "{{ url_for('static', filename='%s') }}" % filename
        elif 'href' in s.attrs and s['href'].startswith('static'):
            without_static = os.path.sep.join(s['href'].split(os.path.sep)[1:])
            filename = os.path.join(user, sitename, without_static)
            s['href'] = "{{ url_for('static', filename='%s') }}" % filename


    return soup, for_db


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '..', '..', 'tests', 'test1.html')) as f:
        template, for_db = parse_html(f.read())