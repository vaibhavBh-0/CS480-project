# CS480-project
Class project for CS480

## Setup instructions

### Install Redis
Follow the instrcutions on https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/

### Start the redis server on terminal
```shell
redis-server
```

### Install Python dependencies
- Create a venv.
```shell
python -m venv movies
movies\bin\activate
```
- Install Python dependencies 

```shell
pip install flask PyMySQL python-dotenv faker Flask-Caching redis cryptography flask-sqlalchemy sqlalchemy
```
Or use the requirements.txt file to install the depenedcies.

```shell
pip install -r requirements.txt
```

### Database stuff pending
Shomee, Peyman you can fill this out.

### Run the flask app
```shell
flask run
```