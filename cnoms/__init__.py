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

    app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))

    return app
