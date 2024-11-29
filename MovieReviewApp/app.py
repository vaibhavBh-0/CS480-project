from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    __table_args__ = (
        db.CheckConstraint("LENGTH(password) >= 8", name='check_password_length'),
    )
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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        db.CheckConstraint('rating BETWEEN 1 AND 10', name='check_rating_range'),
    )
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('casts.id'))
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Movie id: {self.id}"


with app.app_context():
    db.drop_all()
    db.create_all()


@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        new_user = User(
            name=request.form['user_name'],
            email=request.form['user_email'],
            password=request.form['user_password'],
            role=request.form['user_role'],
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding the new user'

    else:
        users = User.query.order_by(User.date_created).all()
        return render_template('index.html', tasks=users)
    

@app.route('/movies', methods=["POST", "GET"])
def movie():
    if request.method == 'POST':
        new_movie = Movie(
            name=request.form['movie_name'],
            budget=float(request.form['movie_budget']),
            revenue=float(request.form['movie_revenue']),
            rating=float(request.form['movie_rating']),
        )

        new_casts = []
        cast_count = len([key for key in request.form.keys() if key.startswith('cast_name_')])
        for i in range(1, cast_count + 1):
            new_cast = Cast(
                name=request.form.get(f'cast_name_{i}'), 
                role=request.form.get(f'cast_role_{i}'),
            )
            new_casts.append(new_cast)

        db.session.add(new_movie)
        db.session.add_all(new_casts)
        db.session.commit()

        new_genre = Genre(
            movie_id = new_movie.id,
            genre = request.form['movie_genre']
        )

        new_participations = []
        for new_cast in new_casts:
            participation = Participation(
                movie_id=new_movie.id, 
                cast_id=new_cast.id
            )
            new_participations.append(participation)

        db.session.add(new_genre)
        db.session.add_all(new_participations)
        db.session.commit()

        return redirect('/movies')
    else:
        movies = Movie.query.order_by(Movie.date_created).all()
        return render_template('movies.html', tasks=movies)

@app.route('/reviews', defaults={'movie_id': None}, methods=["GET", "POST"])
@app.route('/reviews/<int:movie_id>', methods=["GET", "POST"])
@app.route('/reviews', methods=["GET", "POST"])
def reviews():
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
            return redirect('/reviews')  
        except Exception as e:
            return f"There was an issue adding the review: {str(e)}"

    
    reviews = Review.query.order_by(Review.date_created).all()
    movies = Movie.query.all()  
    return render_template('reviews.html', tasks=reviews, movies=movies)


if __name__ == "__main__":
    app.run(debug=True)