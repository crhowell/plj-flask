import datetime

from flask import (Flask, g, render_template, flash, redirect,
                   url_for)

from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, current_user,
                         login_required, logout_user)
import forms
import models

DEBUG = True
HOST = '0.0.0.0'
PORT = 8000


app = Flask(__name__)
app.secret_key = 'lKJlknm12lknasldkjalksjda'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.select().where(
            models.User.id == int(userid)
        ).get()
    except models.DoesNotExist:
        return None


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


@app.route('/list')
@login_required
def entry_list():
    entries = current_user.entries
    return render_template('index.html', entries=entries)


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        models.User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(
                models.User.email == form.email.data
            )
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You're now logged in!")
                return redirect(url_for('index'))
            else:
                flash("No user with that email/password combo")
        except models.DoesNotExist:
            flash("No user with that email/password combo")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    models.initialize()

    app.run(debug=DEBUG, host=HOST, port=PORT)

