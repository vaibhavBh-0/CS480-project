import time
from flask import Flask, render_template, request, redirect, url_for, flash

from flask_caching import Cache
from utils import get_string_date_from_time, format_currency
from sqlalchemy import text
from database_utils import *
from datetime import datetime

cache = Cache(app)

@app.route("/login", methods=["GET", "POST"])
def login_view():
    sign_up = False

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        value = request.form["submission"]
        if value == 'Login':
            # User ID is int.
            verified = result.isnumeric()
            
            if verified:
                user_id = int(result)
                return redirect(url_for('movie_list_view', user_id=user_id))
            else:
                flash('User login not successful! Username or Password is invalid.', 'failed.') 
                return render_template('login_view.html', sign_up=sign_up)
        elif value == 'Signup & login':
            username = request.form["username"]
            result = str(signup(username, user_email=email, user_password=password))
            sign_up = True

            if result.isnumeric():
                user_id = int(result)
                return redirect(url_for('movie_list_view', user_id=user_id))
            else:
                flash('User login not successful! Username or Password is invalid.', 'failed.') 
                return render_template('login_view.html', sign_up=sign_up)
    elif request.method == "GET":
        if 'submission' in request.args:
            # User is trying to sign up.
            value = request.args['submission']
            if value == 'signup':
                sign_up = True

    return render_template('login_view.html', sign_up=sign_up)
    

@app.route("/",methods=["GET", "POST"])
@app.route("/<user_id>",methods=["GET", "POST"])
def movie_list_view(user_id=None):
    # TODO: Saran
    # 1. List the content of all movies. 
    # 2. Navigate to Screen 1 when not logged in, 
    # Screen 3 when selecting a movie, Screen 4 when logged in and user_role is "admin" 
    if request.method == 'POST':
        search_term = request.form.get('search')
        if search_term:
            # Redirect to the GET request with search term and page 1 (for new search)
            return redirect(url_for('movie_list_view', search=search_term, page=1))

    # Get current page and search term from query parameters
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search')
    per_page = 100
    time_start = time.time()

    if search_term:
        movie_data = fetch_movies(search_term)
        movies = []
        for tup in movie_data:
            movies.append({'movie_id': tup[0],
                    'movie_name': tup[1],
                    'movie_budget': tup[2],
                    'movie_revenue': tup[3],
                    'genre': tup[4],
                    'avg_rating': tup[5]})
        # movies = search_books(search_term)
    else:
        # Check if the response is already cached
        # movies = cache.get('movies')
        # # books = cache.get('books')
        # # TODO: When to fetch instead of cache needs to be investigated.
        # if movies:
        #     print("Used cache to fetch from database.")
        if True:
            query_text = text('SELECT * FROM movies')
            movie_data = db.session.execute(query_text).fetchall()
            movies = []
            for tup in movie_data:
                movies.append({'movie_id': tup[0],
                    'movie_name': tup[1],
                    'movie_budget': format_currency(tup[2]),
                    'movie_revenue': format_currency(tup[3]),
                    'genre': tup[4],
                    'avg_rating': tup[5]})
            cache.set("movies", movies)
    admin=0
    if user_id is not None:
        admin = int(user_id == '1')
    else:
        admin = 0
    total_rows = len(movies)
    range_start = (page - 1) * per_page
    range_end = min(page * per_page, total_rows)
    paginated_books = movies[range_start: range_end]
    total_pages = (total_rows + per_page - 1) // per_page
    if user_id is not None:
        print(f'User is logged in {user_id}')
    else:
        print("User is not logged in.")

    return render_template('movie_list_view.html',
                           total_rows=total_rows,
                           books=paginated_books, page=page, total_pages=total_pages,
                           range_start=range_start, range_end=range_end, 
                           search=search_term, user_id=user_id, admin=admin)
    
@app.route("/movie_detail_view/<movie_id>", methods=["GET"])
@app.route("/movie_detail_view/<movie_id>/<user_id>", methods=["GET", "POST"])
def movie_review_details_view(movie_id, user_id=None):
    # print(movie_id, user_id, "Needed")
    # TODO: Vaibhav
    # 1. List Movie details. 
    # 2. List Comments. 
    # 3. If logged in users can view, add or edit their comment. 
    # 4. Navigate back to movie_list_view.

    # Is cache needed here?
    query_text = text(f'SELECT * FROM movies where id={movie_id}')
    movie_details_list = db.session.execute(query_text).fetchall()[0]
    query_text = text(f'SELECT * FROM reviews where movie_id={movie_id}')

    movie_reviews = db.session.execute(query_text).fetchall()   
    update_post_flag = False
    delete_flag = False
    if request.method == "POST":

       if request.form['comment_submission']=='DELETE':
           result = delete_review(movie_id,user_id)
           print(f'Deleing review {result}')
           delete_flag = True
       else:
           if len(movie_reviews)!=0:
               user_id_list = [tup[-2] for tup in movie_reviews]
               update_post_flag = int(user_id) in user_id_list
               for tup in movie_reviews:
                  if tup[-2]==int(user_id):
                    review_id = tup[0]
           if update_post_flag:
               result = update_review(movie_id,user_id,review_id,request.form['comment'],int(request.form['rating']))
               print(f'Result : {review_id}')
           else:
               result = reviews(movie_id,request.form['comment'],int(request.form['rating']),user_id)
               
               # Successful insertion
               if str(result).isnumeric():
                   review_id = int(result)
               else:
                   print('error in updating Review')

           # check if comment is to be updated or deleted.

       # if request.form['comment_submission'] == 'delete':
       #     print("Delete comment")
       # elif request.form['comment_submission'] == 'post':
       #     print("post comment")

    # query_text = text(f'SELECT * FROM movies where id={movie_id}')
    # movie_details_list = db.session.execute(query_text).fetchall()[0]
    query_text = text(f'SELECT * FROM reviews where movie_id={movie_id}')

    movie_reviews = db.session.execute(query_text).fetchall()
    average_rating = sum(item[2] for item in movie_reviews) / len(movie_reviews) if len(movie_reviews) else 0
    if update_post_flag or delete_flag:
        update_movie(movie_id, average_rating)
        # average_rating = 0
        # if len(movie_reviews)!=0:
        #     average_rating = sum(item[2] for item in movie_reviews) / len(movie_reviews)
        #     update_movie(movie_id, average_rating)
        # else:
        #     update_movie(movie_id, average_rating)
    genres = fetch_genre(movie_id)

    movie_details = {
        'movie_id': movie_details_list[0],
        'movie_name': movie_details_list[1],
        'movie_budget': format_currency(movie_details_list[2]),
        'movie_revenue': format_currency(movie_details_list[3]),
        'genre': genres[0][0],
        'avg_rating': average_rating
    }

    movie_comments = []
    for tup in movie_reviews:
        username = fetch_user_name(tup[-2])
        movie_comments.append({'timestamp': int(round(datetime.strptime(tup[-1], "%Y-%m-%d %H:%M:%S.%f").timestamp())),
                'user_id': tup[-2],
                'user_name': username,
                'review_id' : tup[0],
                'movie_id' : tup[-3],
                'comment': tup[1],
                'rating': tup[2]})
    user_comment = None

    if user_id is not None:
        filtered_comments = []

        for comment in movie_comments:
            if comment['user_id'] == int(user_id):
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


@app.route("/add_movie_details_view/<user_id>", methods=["GET", "POST"])
def add_movie_details_view(user_id):
    if request.method == "POST":
        # Successful insertion into the database.
        form = request.form
        # Don't use float('nan')
        invalid_numeric_value = None

        crew_count = len([key for key in form.keys() if 'crew_name' in key])

        if crew_count == 0:
            crew_count = 1
            flash('crew member mismatch', 'failed.')
            return render_template("add_movie_details_view.html", user_id=user_id, crew_count=crew_count)

        form = dict(form)
        movie_name = form["movie_name"]

        # validating numeric fields.
        for key in ['budget', 'revenue']:
            if key in form:
                value = str(form[key])
                if value.isnumeric() or (value.startswith('-') and value[1:].isnumeric()):
                    value = max(int(value), 0)
                    print(value)
                    form[key] = value
                else:
                    flash('Invalid numeric field', 'failed.')
                    return render_template("add_movie_details_view.html", user_id=user_id, crew_count=crew_count)

        movie_budget = form.get("budget", invalid_numeric_value)
        movie_revenue = form.get("revenue", invalid_numeric_value)
        movie_genre = form["genre"]
        movie_rating = 0

        movie_casts = []

        for idx in range(crew_count):
            crew_name_key = f'crew_name_{idx}'
            crew_role_key = f'crew_role_{idx}'
            item = (form[crew_name_key], form[crew_role_key])
            movie_casts.append(item)

        _ = add_movie(movie_name, movie_budget=movie_budget, 
                      movie_revenue=movie_revenue, movie_casts=movie_casts,
                      movie_genre=movie_genre, movie_rating=movie_rating)
        
        print(_)
        
        return redirect(url_for('movie_list_view', user_id=user_id))

    crew_count = int(request.args.get('crew_count', 1))
    return render_template("add_movie_details_view.html", user_id=user_id, crew_count=crew_count)