import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash

from dotenv import load_dotenv
from flask_caching import Cache

from utils import get_string_date_from_time


if not load_dotenv('.flashenv'):
    print("Environment var not found")

app = Flask(__name__)
# Set environment variables and secrets.
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["CACHE_TYPE"] = os.getenv("CACHE_TYPE")
app.config["CACHE_REDIS_HOST"] = os.getenv("CACHE_REDIS_HOST")
val = os.getenv("CACHE_REDIS_PORT")
print(f'val: {val} and type: {type(val)}')
app.config["CACHE_REDIS_PORT"] = int(os.getenv("CACHE_REDIS_PORT"))
app.config["CACHE_DEFAULT_TIMEOUT"] = int(os.getenv("CACHE_DEFAULT_TIMEOUT"))
app.config["CACHE_REDIS_DB"] = int(os.getenv("CACHE_REDIS_DB"))

cache = Cache(app)

@app.route("/login", methods=["GET", "POST"])
def login_view():
    # TODO:
    # 1. Connect to user table to verify correct username and/or password. - Shomee, Peyman
    # 2. Pass the user_info to previous screen. - Vaibhav
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
         # TODO: (1.) We assume it's verfied for now.
        verified = True
       
        if verified:
            user_info = {
                "user_id" : "1234",
                "user_role": "general_user"
            }

            # Other examples
            # user_info = {
            #     "user_id" : "1234",
            #     "user_role": "admin"
            # }

            # TODO: (2.) Route to previous screen - wherever the login view was called.
            # return redirect(url_for('movie_review_details_view', movie_id="69", user_id=user_info['user_id']))
            return render_template('login_successful.html', user_info=user_info)
        else:
            flash('User login not successful! Username or Password is invalid.', 'failed.') 
            return render_template('login_view.html')
    elif request.method == "GET":
        return render_template('login_view.html')
    

@app.route("/")
def movie_list_view():
    # TODO: Saran
    # 1. List the content of all movies. 
    # 2. Navigate to Screen 1 when not logged in, 
    # Screen 3 when selecting a movie, Screen 4 when logged in and user_role is "admin" 
    return render_template("movie_list_view.html")
    
@app.route("/movie_detail_view/<movie_id>", methods=["GET"])
@app.route("/movie_detail_view/<movie_id>/<user_id>", methods=["GET", "POST"])
def movie_review_details_view(movie_id, user_id=None):
    # TODO: Vaibhav
    # 1. List Movie details. 
    # 2. List Comments. 
    # 3. If logged in users can view, add or edit their comment. 
    # 4. Navigate back to movie_list_view.

    # Is cache needed here?

    if request.method == "POST":
       # TODO: Insert into movie reviews.

       # check if comment is to be updated or deleted.
       if request.form['comment_submission'] == 'delete':
           print("Delete comment")
       elif request.form['comment_submission'] == 'post':
           print("post comment")


    movie_details_key = f'movie_details_{movie_id}'
    movie_reviews_key = f'movie_reviews_key{movie_id}'
    movie_details = cache.get(movie_details_key)
    movie_comments = cache.get(movie_reviews_key)

    debug = True

    if movie_details is None:
        # Call the query and set it in cache.
        pass

    if movie_comments is None:
        # Call the query and set it in cache.
        pass

    if debug:
        movie_details = {
            'movie_id': '1234',
            'movie_name': 'The Shawshank Redemption',
            'movie_budget': '$25 million',
            'movie_revenue': '$73.3 million',
            'genre': 'Escape from Prison',
            'avg_rating': '4.8/5.0'
        }

        now = time.time()
        in_minutes = lambda x: x * 60

        movie_comments = [  {
                'timestamp': now - in_minutes(60),
                'user_id' : '123',
                'review_id' : '1',
                'movie_id' : '1234',
                'comment': "A masterpiece!",
                'rating': '4.8/5.0'
            },
            {
                'timestamp': now - in_minutes(25),
                'user_id' : '125',
                'review_id' : '2',
                'movie_id' : '1234',
                'comment': "A masterpiece!",
                'rating': '4.8/5.0'
            },
            {
                'timestamp': now - in_minutes(30),
                'user_id' : '1234',
                'review_id' : '3',
                'movie_id' : '1234',
                 'comment': "A masterpiece!",
                'rating': '4.8/5.0'
            }
        ]

    user_comment = None

    if user_id is not None:
        filtered_comments = []

        for comment in movie_comments:
            if comment['user_id'] == user_id:
                user_comment = comment
            else:
                filtered_comments.append(comment)

        movie_comments = filtered_comments

    # Assume movie_comments are not sorted by timestamp.
    movie_comments = sorted(movie_comments, key=lambda x: x['timestamp'], reverse=True)

    for movie_comment in movie_comments:
        movie_comment['timestamp'] = get_string_date_from_time(movie_comment['timestamp'])

    if user_comment is not None:
        user_comment['timestamp'] = get_string_date_from_time(user_comment['timestamp'])
        # TODO: render page differently.

    return render_template("movie_review_details_view.html", 
                           movie_details=movie_details,
                           user_id = user_id, 
                           user_comment=user_comment,
                           movie_comments=movie_comments)


