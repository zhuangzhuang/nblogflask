#coding: utf8
from hashlib import md5
import datetime
from nblog import app, db


class User(db.Document):
    name = db.StringField(required=True)
    password = db.StringField(required=True)
    email = db.StringField(required=True)

    def __repr__(self):
        return "<User: %s>" % (self.name)


class Post(db.Document):
    name = db.StringField(required=True)
    title = db.StringField(required=True)
    post = db.StringField(required=True)
    time = db.DateTimeField(default=datetime.datetime.now)

    def __repr__(self):
        return "<Post: %s>" % (self.title)
