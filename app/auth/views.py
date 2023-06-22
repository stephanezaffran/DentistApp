from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import auth_blueprint
from app.forms import LoginForm, UserForm
from app.models import User, db

from functools import wraps


def login_and_referer_required(func):
    @wraps(func)
    @login_required
    def decorated_view(*args, **kwargs):
        # Check if the request originates from the application
        if not request.referrer or not request.referrer.startswith(request.host_url):
            flash('Unauthorized access. Please access the page through the application.', 'error')
            return redirect(url_for('auth.logout'))

        return func(*args, **kwargs)

    return decorated_view

# def login_required(route):
#     @wraps(route)
#     def decorated_function(*args, **kwargs):
#         referer = request.headers.get('Referer')
#         print(f"referrer : {referer}")
#         if not current_user.is_authenticated or referer is None:  #or referrer is None:
#             return redirect('/login')
#         return route(*args, **kwargs)
#     return decorated_function
#


@auth_blueprint.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()

    if form.validate_on_submit():
        print("entered to validate_on_submit ")
        username = form.username.data
        password = form.password.data
        form.process()
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            print(current_user)

            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password.', 'error')

    else:
        print(f'{form.password} {form.username}')

    return render_template('login.html', form=form)


@auth_blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_blueprint.route('/add_user', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        password = form.password.data
        user = User(name=name, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template('add_user.html', form=form)
