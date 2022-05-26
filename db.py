from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from user import User

client = MongoClient("mongodb+srv://jessicacosta:<VjRi9WDjH54nhhE>@clustercd.vsbbn.mongodb.net/?retryWrites=true&w=majority")

chat_db = client.get_database("chatApp")
users_collection = chat_db.get_collection("user")

def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})


def get_user(username):
    user_data = users_collection.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None

save_user('rrrrr','jessica@gmail.com', 'asdhbbe')
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from werkzeug.security import generate_password_hash
# from user import User
# app = Flask(__name__)
#
#
# class Student(db.Model):
#     __tablename__ = "users"
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(25), unique=True, nullable=False)
#     hashed_pswd = db.Column(db.String(), nullable=False)
#
#
# def save_user(username, email, password):
#     password_hash = generate_password_hash(password)
#     db.session.add({'_id': username, 'email': email, 'password': password_hash})
#
#
# def get_user(username):
#     user_data = db.session.find_one({'_id': username})
#     return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None