import flask_login
from .app import db
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .utils import signups_allowed

# initialize auth routes
auth = Blueprint('auth', __name__)

# basic login page route
@auth.route('/login')
def login():
    return render_template('login.html')

# route for posting user-supplied input to app
@auth.route('/login', methods=['POST'])
def login_post():
    # assign user input to variables
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        # return the user to login page if details do not match
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    # log the user into the app if details do match
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


# allow a user to be added to the database
@auth.route('/signup')
def signup():
    if signups_allowed() == 1:
        return render_template('signup.html', name="Anonymous")
    elif signups_allowed() == 0:
        if current_user.is_authenticated:
            if current_user.is_admin:
                return render_template('signup.html', name=current_user.name)
        else:
            return redirect(url_for('auth.login'))

# accept user input to be added to the database
@auth.route('/signup', methods=['POST'])
def signup_post():
    if signups_allowed() == 0:
        if not current_user.is_admin:
            abort(401)
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    is_admin = True if request.form.get('is_admin') else False

    user = User.query.filter_by(
        email=email).first()

    if user:
        flash('Email already registered.')
        return redirect(url_for('auth.signup'))

    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), is_admin=is_admin)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

# log the user out of the app
@auth.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logout'

# allow admins to view and manage users
@auth.route('/usermanager')
@login_required
def usermanager():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return render_template('manager-users.html', title="User Management Coming Soon!", users=User.query.all(), name=current_user.name)
    return redirect(url_for('auth.login'))
