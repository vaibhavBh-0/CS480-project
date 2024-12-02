import os
from flask import Flask

app = None

def get_app_config():
    global app
    if app is None:
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
        return app
    else:
        print("App is already configured")
        return app
    