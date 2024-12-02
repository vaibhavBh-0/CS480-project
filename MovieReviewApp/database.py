from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime
from dotenv import load_dotenv

from app_singleton import get_app_config

if not load_dotenv('.flashenv'):
    print("Environment var not found")

# app = Flask(__name__)
app = get_app_config()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    # __table_args__ = (
    #     db.CheckConstraint("LENGTH(password) >= 8", name='check_password_length'),
    # )
    role = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"User id: {self.id}"
    

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Numeric(15, 2))
    revenue = db.Column(db.Numeric(15, 2))
    genre = db.Column(db.String(50))
    rating = db.Column(db.Numeric(2, 1))

    # cast_members = db.relationship('Cast', backref='movie', lazy=True)  # This lets each movie to keep track of its casts
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Movie id: {self.id}"


class Cast(db.Model):
    __tablename__ = 'casts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Cast id: {self.id}"
    

class Participation(db.Model):
    __tablename__ = 'participations'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    cast_id = db.Column(db.Integer, db.ForeignKey('casts.id'), primary_key=True)


class Genre(db.Model):
    __tablename__ = 'genres'
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    genre = db.Column(db.String(20), primary_key=True)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(50))
    rating = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.CheckConstraint('rating BETWEEN 1 AND 10', name='check_rating_range'),
    )
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('casts.id'), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Movie id: {self.id}"