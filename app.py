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
    return redirect(url_for('entry_list'))


@app.route('/entries/edit/<int:entry_id>', methods=('GET', 'POST'))
@login_required
def entry_edit(entry_id=None):
    if entry_id is not None:
        try:
            entry = models.Entry.get(id=entry_id)
            form = forms.EntryForm()

            if form.validate_on_submit():
                if entry.user == current_user:
                    entry.title = form.title.data
                    entry.date = form.date.data
                    entry.time_spent = form.time_spent.data
                    entry.learned = form.learned.data
                    entry.resources = form.resources.data
                    entry.tags = form.tags.data
                    entry.save()
                    return redirect(url_for('entry_detail', entry_id=entry.id))
                flash('warning', 'You are not the owner of this entry.')
                return redirect(url_for('entry_detail', entry_id=entry.id))

            form.title.data = entry.title
            form.date.data = entry.date
            form.time_spent.data = entry.time_spent
            form.learned.data = entry.learned
            form.resources.data = entry.resources
            form.tags.data = entry.tags

            return render_template('edit.html', form=form, entry_id=entry_id)

        except models.DoesNotExist:
            flash('warning', 'That entry does not exist.')
    return redirect(url_for('entry_list'))


@app.route('/entries/<int:entry_id>')
def entry_detail(entry_id=None):
    if entry_id is not None:
        try:
            entry = models.Entry.get(id=entry_id)
            return render_template('detail.html', entry=entry)
        except models.DoesNotExist:
            flash('warning', 'That entry does not exist.')
            return redirect(url_for('entry_list'))
    return redirect(url_for('entry_list'))


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new_entry():
    form = forms.EntryForm()
    if form.validate_on_submit():
        models.Entry.create(user=g.user._get_current_object(),
                            title=form.title.data,
                            date=form.date.data,
                            time_spent=form.time_spent.data,
                            learned=form.learned.data.strip(),
                            resources=form.resources.data.strip(),
                            tags=form.tags.data)
        flash("Entry Added!", "success")
        return redirect(url_for('entry_list'))

    return render_template('new.html', form=form)


@app.route('/entries')
def entry_list():
    entries = models.Entry.select()
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
                return redirect(url_for('entry_list'))
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

