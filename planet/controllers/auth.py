from flask import g, Blueprint, flash, redirect, url_for, render_template, request
from flask.ext.login import current_user, login_user, logout_user, login_required

from planet import login_manager
from planet.models.users import User
from planet.forms.login import LoginForm
from planet.forms.registration import RegistrationForm
from planet import db

from datetime import datetime


auth = Blueprint('auth', __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth.before_request
def get_current_user():
    g.user = current_user


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    function to register a user
    """
    if current_user.is_authenticated():
        flash('You are already logged in.', 'warning')
        return redirect(url_for('main.screen'))

    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        existing_username = User.query.filter_by(username=username).first()

        if existing_username:
            flash('This username has been already taken. Try another one.', 'warning')
            return render_template('register.html', form=form)

        user = User(username, password, email, '', False, False, datetime.now().replace(microsecond=0))

        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()

        flash('You are now registered. Please login.', 'success')

        return redirect(url_for('auth.login'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    function to check a user's credentials and log him in
    """
    if current_user.is_authenticated():
        flash('You are already logged in.')
        return redirect(url_for('main.screen'))

    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        username = request.form.get('username')
        password = request.form.get('password')
        keep_logged = True if request.form.get('keep_logged') == 'y' else False
        existing_user = User.query.filter_by(username=username).first()

        if not (existing_user and existing_user.check_password(password)):
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html', form=form)

        login_user(existing_user, remember=keep_logged)
        flash('You have successfully logged in.', 'success')
        return redirect(url_for('main.screen'))

    if form.errors:
        flash(form.errors, 'danger')

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    flash('You have successfully logged out.', 'success')
    logout_user()
    return redirect(url_for('main.screen'))
