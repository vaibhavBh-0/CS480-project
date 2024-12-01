from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime
from database import *
import re


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

with app.app_context():
    db.drop_all()
    db.create_all()

ADMIN_NAME = 'ADMIN'
ADMIN_EMAIL = 'ADMIN_PASSWORD'
ADMIN_PASSWORD = '123456789'
admin_user = User(
    name=ADMIN_NAME,
    email=ADMIN_EMAIL,
    password=ADMIN_PASSWORD,
    role='admin',
)
db.session.add(admin_user)
db.session.commit()


def fetch_user(email):
    return User.query.filter_by(email=email).first()


def is_valid_email_format(email):
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None


def fetch_movies_by_name(substring):
    return Movie.query.filter(Movie.name.ilike(f"%{substring}%")).all()


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
    for i in range(1, len(movie_casts) + 1):
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
    return [movie.id for movie in movies]


@app.route('/reviews', defaults={'movie_id': None}, methods=["GET", "POST"])
def reviews(movie_id):
    if request.method == "POST":
       
        new_review = Review(
            content=request.form['review_content'], 
            rating=int(request.form['review_rating']), 
            movie_id=request.form['movie_id'], 
            user_id=request.form['user_id'],  
        )
        try:
            db.session.add(new_review)
            db.session.commit()
            movie = Movie.query.get(movie_id)
            reviews = Review.query.filter_by(movie_id=movie_id).all()
            average_rating = (sum([review.rating for review in reviews]) / len(reviews))
            movie.rating = round(average_rating, 1) 
            db.session.commit()

            return redirect('/reviews')  
        except Exception as e:
            return f"There was an issue adding the review: {str(e)}"

    
    reviews = Review.query.order_by(Review.date_created).all()
    movies = Movie.query.all()  
    return render_template('reviews.html', tasks=reviews, movies=movies)
def update_review():
    if request.method == "POST":
        movie_id = int(request.form['movie_id'])
        user_id = int(request.form['user_id'])
        
        review = Review.query.filter_by(movie_id=movie_id, user_id=user_id).first()
        if not review:
            return "Error"

        
        review.content = request.form['updated_review']
        review.rating = int(request.form['updated_rating'])
            
        db.session.commit()

            
        movie = Movie.query.get(movie_id)
        if movie:
                reviews = Review.query.filter_by(movie_id=movie_id).all()
                average_rating = sum([r.rating for r in reviews]) / len(reviews)
                movie.rating = round(average_rating, 1)
                db.session.commit()
            
        return redirect('/reviews')
def delete_review():
    if request.method == "POST":
       
        movie_id = int(request.form['movie_id'])
        user_id = int(request.form['user_id'])
        

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
                    movie.ratin=None
                    
            
            return redirect('/reviews')

if __name__ == "__main__":
    app.run(debug=True)