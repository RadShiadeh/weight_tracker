from flask import Flask, jsonify, request, session, redirect, url_for
import mongoengine as me
from users_data import models
import bcrypt
from app import db
import re
from helper import helpers


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

    def start_session(self, user):
        del user["password"]
        session['logged_in'] = True
        session["user"] = user
        session["start_key"] = request.form.get('plot-from', "")
        session["end_key"] = request.form.get('plot-to', "")
        session["selected_plot_data"] = 'all_weights'
        session["data"] = {}
        session["chart_title"] = ""
        session["nw_dup"] = 0
        session["date_dup"] = ""

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
            "all_weights": {},
            "weekly_avgs": {},
            "last_seven": []
        }

        collection = db["users"]
        user = collection.find_one({"username": user_json["username"]})

        if user:
            if bcrypt.checkpw(user_json["password"].encode('utf-8'), user["password"].encode('utf-8')):
                user_json["username"] = user["username"]
                user_json["email"] = user["email"]
                user_json["all_weights"] = user["all_weights"]
                user_json["weekly_avgs"] = user["weekly_avgs"]
                user_json["last_seven"] = user["last_seven"]

                return self.start_session(user_json)
            else:
                return jsonify({"error": "wrong password"}), 400
        else:
            return jsonify({"error": "Invalid username or password"}), 400
    
    def update_entry(self, session, date, entry):
        entry = float(entry)
        all_weights = session["user"]["all_weights"]
        all_weekly_averages = session["user"]["weekly_avgs"]
        last_seven = session["user"]["last_seven"]
        collection = db["users"]
        user_name = session["user"]["username"]

        all_weights_c = {}
        for w in all_weights:
            all_weights_c[w["date"]] = [float(w["weight"][0]), int(w["weight"][1])]

        all_weekly_averages_c = {}
        for w in all_weekly_averages:
            all_weekly_averages_c[w["date"]] = [float(w["average"]), int(w["index"])]
        
        last_seven[0]['index'] = int(last_seven[0]['index'])
        for k, v in last_seven[0]['data'].items():
            last_seven[0]['data'][k] = float(v)

        
        all_weights, last_seven, all_weekly_averages, _ = helpers.update_local_enteries(last_seven, entry, all_weekly_averages_c, all_weights_c, date)
        helpers.update_db(all_weights, all_weekly_averages, last_seven, collection, user_name)

        return redirect(url_for('index'))