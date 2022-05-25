from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from user import User
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:8m4Q4634@localhost/chatApp'
class Student(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    hashed_pswd = db.Column(db.String(), nullable=False)


def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    db.session.add({'_id': username, 'email': email, 'password': password_hash})


def get_user(username):
    user_data = db.session.find_one({'_id': username})
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None