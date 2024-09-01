from flask import request, session
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

@app.route('/update_entry', methods=["POST"])
def update_entry():
    date = request.form.get('date_rep')
    entry = request.form.get('new_weight_rep')

    return User().update_entry(session, date, entry)



@app.route('/users/data/<username>', methods=["GET"])
def get_user_data(username):
    return User().get_user_data(username)



@app.route('/users/data/<username>', methods=["PUT"])
def update_user(username):
    return User().update_user(username)



@app.route('/users/data/<username>', methods=["DELETE"])
def delete_user(username):
    return User().delete_user(username)  