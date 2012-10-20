from flask import Flask
from flask_peewee.db import Database
import config

app = None
db = None

def create_app(local=True):
    global app
    global db
    app = Flask(__name__)
    config_obj = config.Local if local else config.Base
    app.config.from_object(config_obj)
    db = Database(app)
    return app
