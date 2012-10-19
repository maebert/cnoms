#!/usr/bin/env python
# encoding: utf-8
"""
    parse what we get from the user
"""

import sys, os
from bs4 import BeautifulSoup
import re

def parse_html(html_doc):
    """ return the template and a list of dictionaries with the
        containing all information we have to add to the database
    """
    for_db = []
    soup = BeautifulSoup(html_doc)
    for s in soup.find_all(True):
        if 'data-fieldname' in s.attrs:
            tmp = {'fieldname': s.attrs['data-fieldname'],
                   'type': s.attrs.get('data-type', 'plain'),
                   'value': s.get_text()}
            for_db.append(tmp)
            s.clear()
            s.insert(0, '{{ ' + s.attrs['data-fieldname'] + ' }}')
    return soup, for_db


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    with open(os.path.join(path, '..', '..', 'tests', 'test1.html')) as f:
        template, for_db = parse_html(f.read())