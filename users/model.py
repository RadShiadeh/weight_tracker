from flask import Flask, jsonify, request, session, redirect
import mongoengine as me
from users_data import models
import bcrypt
from app import db
import re


class User(me.Document):
    username = me.StringField(required=True, unique=True)
    password = me.StringField(required=True)
    email = me.EmailField(required=True, unique=True)
    all_weights = me.ListField(me.EmbeddedDocumentField(models.AllWeights), default = [])
    weekly_avgs = me.ListField(me.EmbeddedDocumentField(models.WeeklyAverages), default = [])
    last_seven = me.ListField(me.EmbeddedDocumentField(models.LastSeven), default = [])

    meta = {
        'collection': 'users', #change this for prod
        'indexes': ['username', 'email']
    }

    def start_session(self, user):
        del user["password"]
        session['logged_in'] = True
        session["user"] = user
        return user, 200

    def has_sql_keywords(self, input_str):
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'TRUNCATE', 'ALTER']
        pattern = re.compile('|'.join(sql_keywords), re.IGNORECASE)
        return bool(pattern.search(input_str))

    
    def signup(self):
        user_json = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "email": request.form.get("email"),
            "all_weights": self.all_weights,
            "weekly_avgs": self.weekly_avgs,
            "last_seven": self.last_seven
        }

        if any(self.has_sql_keywords(user_json[field]) for field in ['username', 'email', 'password']):
            return jsonify({"error": "Invalid input detected, you are using reserved key words in your email, password or username"}), 400

        if len(user_json["password"]) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400

        if len(user_json["username"]) < 4:
            return jsonify({"error": "username must be at least 4 characters long"}), 400

        confirmed_pass = request.form.get("confirm")

        if confirmed_pass != user_json['password']:
            return jsonify({"error": "Passwords do not match"}), 400

        collection = db["users"]

        if collection.find_one({"username": user_json["username"]}):
            return jsonify({"error": "Username already in use"}), 400

        if collection.find_one({"email": user_json["email"]}):
            return jsonify({"error": "Email already in use"}), 400
        
        user_json["password"] = bcrypt.hashpw(str.encode(user_json["password"], 'utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(username=user_json["username"],
                        password=user_json["password"],
                        email=user_json["email"],
                        all_weights=user_json["all_weights"],
                        weekly_avgs=user_json["weekly_avgs"],
                        last_seven=user_json["last_seven"])

        if collection.insert_one(new_user.to_mongo()):
            return self.start_session(user=user_json)

        return jsonify({"error": "signup failed"}), 400
    
    def signout(self):
        session.clear()
        return redirect('/')

    
    def login(self):
        user_json = {
            "username": request.form.get("username"),
            "password": request.form.get("password"),
            "all_weights": [],
            "weekly_avgs": [],
            "last_seven": []
        }

        collection = db["users"]
        user = collection.find_one({"username": user_json["username"]})
        user_json["username"] = user["username"]
        user_json["email"] = user["email"]
        user_json["all_weights"] = user["all_weights"]
        user_json["weekly_avgs"] = user["weekly_avgs"]
        user_json["last_seven"] = user["last_seven"]

        if user:
            return self.start_session(user_json)
        else:
            return jsonify({"error": "Invalid username or password"}), 400