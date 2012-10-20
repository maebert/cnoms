#!/usr/bin/env python
# encoding: utf-8
"""
    some utilities
"""

import requests
import watchdog
from cnoms import app

class WatchChanges(watchdog.events.FileSystemEventHandler):

    def __init__(self, folder):
        """docstring for __init__"""
        self.folder = folder

    def on_any_event(self, event):
        print 'changes on the filesystem'
        data = {'user': 'localuser', 'path_to_site': self.folder}
        url = "http://{}:{}/import_website".format(app.config['HOST'],
                                                   app.config['PORT'])
        requests.post(url, params=data)
