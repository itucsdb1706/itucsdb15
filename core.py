from flask import Blueprint
from flask import render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app
from flask import request
from flask_login.utils import login_required, login_user, current_user, logout_user

from models.users import Users

core = Blueprint('core', __name__)


@core.route('/')
def home():
    return render_template('home.html')


@core.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '-')
    password = request.form.get('password', '-')
    user = Users.get(user_id=5)
    print('DBEUBDUEBEDUBUEDBUED ->', user)

    if user is not None and user.check_password(password):
        login_user(user)

    return redirect(request.referrer)


@core.route('/logout')
def logout():

    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('core.home'))


@core.route('/profile')
def profile():
    return render_template('profile-page.html')


@core.route('/register')
def register():
    return render_template('register-page.html')


@core.route('/edit-profile')
def editprofile():
    return render_template('profile-edit.html')


@core.route('/problemlist')
def problemlist():
    return render_template('problems.html')


@core.route('/statement')
def statement():
    return render_template('statement.html')
