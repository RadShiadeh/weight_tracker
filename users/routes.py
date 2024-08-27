from flask import Flask, jsonify, request, session
from app import app, db
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


@app.route('/users/data/<username>', methods=["GET"])
def get_user_data(username):
    collection = db["users"]
    try:
        user_data = collection.find_one({"username": username})
        if user_data:
            user_data['_id'] = str(user_data['_id'])
            del user_data['password']
            return jsonify(user_data), 200
        else:
            return jsonify({"error": f"{username} not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/data/<username>', methods=["PUT"])
def update_user(username):
    collection = db["users"]
    new_data = request.get_json()
    
    try:
        res = collection.update_one({"username": username}, {"$set": new_data})
        if res.matched_count > 0:
            return jsonify({"message": f"Updated {username} with {new_data}"}), 200
        else:
            return jsonify({"error": f"{username} not found"}), 404
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/data/<username>', methods=["DELETE"])
def delete_user(username):
    collection = db["users"]
    try:
        res = collection.delete_one({"username": username})
        if res.deleted_count > 0:
            return jsonify({"message": f"deleted {username}"}), 200
        else:
            return jsonify({"error:" f"{username} not found"}), 404
        
    except Exception as e:
        return jsonify({"error": f"{str(e)}"}), 500
    