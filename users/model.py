from flask import Flask, jsonify
import mongoengine as me
from users_data import models
import bcrypt


class User(me.Document):
    username = me.StringField(required=True, unique=True)
    password = me.StringField(required=True)
    email = me.EmailField(required=True, unique=True)
    all_weights = me.ListField(me.EmbeddedDocumentField(models.AllWeights), default = [])
    weekly_avgs = me.ListField(me.EmbeddedDocumentField(models.WeeklyAverages), default = [])
    last_seven = me.ListField(me.EmbeddedDocumentField(models.LastSeven), default = [])

    meta = {
        'collection': 'users',
        'indexes': ['username', 'email']
    }

    def clean(self):
        if self._created or self._changed_fields:
            self.password = bcrypt.hashpw(str.encode(self.password, 'utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def signup(self):
        return
    
    def login(self):
        return


    def user_details(self):
        user = {
            "_id": "",
            "username": "self.username",
            "email": "self.email"
        }
        return jsonify(user), 200