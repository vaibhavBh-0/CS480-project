# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
# from datetime import datetime
# from .flashenv import *
from database import *
import re
import os

reset_database_flag = int(os.getenv('RESET_DATABASE', 1))

if reset_database_flag:
    with app.app_context():
        db.drop_all()
        db.create_all()
        admin_user = User(
            name=os.getenv('ADMIN_NAME'),
            email=os.getenv('ADMIN_EMAIL'),
            password=os.getenv('ADMIN_PASSWORD'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()


def fetch_user(email):
    return User.query.filter_by(email=email).first()


def fetch_user_name(user_id):
    return User.query.filter_by(id=user_id).first().name


def is_valid_email_format(email):

    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def fetch_movies_by_name(substring):
    query_text = text(f"SELECT * FROM movies WHERE name LIKE '%{substring}%';")
    movie_data = db.session.execute(query_text).fetchall()
    return movie_data


def signup(user_name, user_email, user_password):

    if fetch_user(user_email) is not None:
        return "User exists!"
    
    if not is_valid_email_format(user_email):
        return "Please input a valid email"
    
    new_user = User(
        name=user_name,
        email=user_email,
        password=user_password,
        role='user',
    )

    db.session.add(new_user)
    db.session.commit()
    return new_user.id


def login(user_email, user_password):

    user = fetch_user(user_email)
    if user is None:
        return "User doesn't exists!"
    
    if user.password != user_password:
        return "Password mismatches!"

    return user.id
    

def add_movie(movie_name, movie_budget, movie_revenue, movie_casts, movie_genre="drama", movie_rating=0.0):
    new_movie = Movie(
        name=movie_name,
        budget=movie_budget,
        revenue=movie_revenue,
        rating=movie_rating,
    )

    new_casts = []
    for i in range(len(movie_casts)):
        new_cast = Cast(
            name=movie_casts[i][0], 
            role=movie_casts[i][1],
        )
        new_casts.append(new_cast)

    db.session.add(new_movie)
    has_casts = False
    if len(new_casts) > 0:
        has_casts = True
        db.session.add_all(new_casts)
    db.session.commit()

    new_genre = Genre(
        movie_id = new_movie.id,
        genre = movie_genre
    )

    casts_ids = []
    if has_casts:
        new_participations = []
        for new_cast in new_casts:
            participation = Participation(
                movie_id=new_movie.id, 
                cast_id=new_cast.id
            )
            casts_ids.append(new_cast.id)
            new_participations.append(participation)

    db.session.add(new_genre)
    if has_casts:
        db.session.add_all(new_participations)
    db.session.commit()

    return new_movie.id, casts_ids


def fetch_movies(movie_name):
    movies = fetch_movies_by_name(movie_name)
    return movies

def fetch_genre(movie_id):
    
    query_text = text(f"SELECT genre FROM genres WHERE movie_id = {movie_id};")
    genre_list = db.session.execute(query_text).fetchall() 
    return genre_list

def reviews(movie_id,review_content,rating,user_id):
    new_review = Review(
        id = str(movie_id)+str(user_id),
        content=review_content, 
        rating=rating, 
        movie_id=movie_id, 
        user_id=user_id,  
    )
    try:
        db.session.add(new_review)
        db.session.commit()
        movie = Movie.query.get(movie_id)
        reviews = Review.query.filter_by(movie_id=movie_id).all()
        average_rating = (sum([review.rating for review in reviews]) / len(reviews))
        movie.rating = round(average_rating, 1) 
        db.session.commit()

        return new_review.id  
    except Exception as e:
        return f"There was an issue adding the review: {str(e)}"

def update_movie(movie_id, updated_rating):
    query_text = text(f"UPDATE movies SET rating = {updated_rating} WHERE id = {movie_id};")
    db.session.execute(query_text)
    db.session.commit()

    
def update_review(movie_id,user_id, review_id, updated_review,updated_rating):
    movie_id = movie_id
    user_id = user_id

    query_text = text(f"UPDATE reviews SET content = '{updated_review}', rating = {updated_rating} WHERE id = {review_id};")
    db.session.execute(query_text)
    db.session.commit()

    review = Review.query.filter_by(id=review_id).first()
    if not review:
        return "Error"

    
    review.content = updated_review
    review.rating = updated_rating
        
    db.session.commit()

        
    movie = Movie.query.get(movie_id)
    if movie:
            reviews = Review.query.filter_by(movie_id=movie_id).all()
            average_rating = sum([r.rating for r in reviews]) / len(reviews)
            movie.rating = round(average_rating, 1)
            db.session.commit()
    else:
        return "Movie not found Error"

    return review_id

            
        
def delete_review(movie_id,user_id):
    movie_id = movie_id
    user_id = user_id
    

    review = Review.query.filter_by(movie_id=movie_id, user_id=user_id).first()
    if not review:
        return "Error!"

    
    db.session.delete(review)
    db.session.commit()

        
    movie = Movie.query.get(movie_id)
    if movie:
        reviews = Review.query.filter_by(movie_id=movie_id).all()
        if reviews:
                average_rating = sum([r.rating for r in reviews]) / len(reviews)
                movie.rating = round(average_rating, 1)
        else:
                movie.rating = 0
    else:
        return "Movie error not found!"
    
    return 1


def fetch_review(movie_id):
    return Review.query.filter_by(movie_id=movie_id).all()
