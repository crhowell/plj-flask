import datetime

from flask import (Flask, g, render_template, flash, redirect,
                   url_for)

from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, current_user,
                         login_required, logout_user)

import models

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000


app = Flask(__name__)
app.secret_key = 'lKJlknm12lknasldkjalksjda'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    models.initialize()
    app.run(debug=DEBUG, host=HOST, port=PORT)

