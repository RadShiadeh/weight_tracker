from flask import Flask
from app import app
from users.model import User

@app.route('/users/signup', methods=["GET"])
def signup():
    return User().user_details()