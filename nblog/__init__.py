from flask import Flask
from flask.ext.mongoengine import MongoEngine, MongoEngineSessionInterface
from config import mongo_param

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['MONGODB_SETTINGS'] = mongo_param

db = MongoEngine(app)
app.session_interface = MongoEngineSessionInterface(db)

from views import *