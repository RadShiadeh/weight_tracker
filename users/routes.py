from flask import Flask
from app import app
from users.model import User

@app.route('/users/signup', methods=["POST"])
def signup():
    return User().signup()

@app.route('/users/signout')
def signout():
    return User().signout()

@app.route('/users/login', methods=["POST"])
def login():
    return User().login()