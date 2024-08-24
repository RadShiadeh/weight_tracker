from flask import Flask
from app import app
from users.model import User

@app.route('/users/signup', methods=["POST"])
def signup():
    return User().signup()

@app.route('/users/singout')
def signout():
    return User().signout()