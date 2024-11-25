import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash

from dotenv import load_dotenv
from flask_caching import Cache


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
    
@app.route("/")
def movie_review_details_view():
    # TODO: Vaibhav
    # 1. List Movie details. 
    # 2. List Comments. 
    # 3. If logged in users can view, add or edit their comment. 
    # 4. Navigate back to movie_list_view.
    return render_template("movie_review_details_view.html")


