from flask import Flask, jsonify, request
import mongoengine as me
from users_data import models
import bcrypt
from app import db


class User(me.Document):
    username = me.StringField(required=True, unique=True)
    password = me.StringField(required=True)
    email = me.EmailField(required=True, unique=True)
    all_weights = me.ListField(me.EmbeddedDocumentField(models.AllWeights), default = [])
    weekly_avgs = me.ListField(me.EmbeddedDocumentField(models.WeeklyAverages), default = [])
    last_seven = me.ListField(me.EmbeddedDocumentField(models.LastSeven), default = [])

    meta = {
        'collection': 'users_signup_test', #change this for prod
        'indexes': ['username', 'email']
    }

    def clean(self):
        if self._created or self._changed_fields:
            self.password = bcrypt.hashpw(str.encode(self.password, 'utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def signup(self):
        user_json = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "email": request.form.get("email"),
            "all_weights": self.all_weights,
            "weekly_avgs": self.weekly_avgs,
            "last_seven": self.last_seven
        }

        new_user = User(username=user_json["username"],
                        password=user_json["password"],
                        email=user_json["email"],
                        all_weights=user_json["all_weights"],
                        weekly_avgs=user_json["weekly_avgs"],
                        last_seven=user_json["last_seven"])
        
        collection = db["users_signup_test"]
        collection.insert_one(new_user.to_mongo())

        return user_json
    
    def login(self):
        return