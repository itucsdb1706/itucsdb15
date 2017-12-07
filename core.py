from flask import Blueprint
from flask import render_template
from flask import redirect, request, url_for
from flask.helpers import url_for
from flask import current_app
from flask import request
from flask_login.utils import login_user, current_user, logout_user

from models.users import Users
from utils import login_required

core = Blueprint('core', __name__)


@core.route('/')
def home():
    return render_template('home.html')


@core.route('/login', methods=['POST'])
def login():
    email = request.form.get('email', '-')
    password = request.form.get('password', '-')
    user = Users.get(email=email)[0]
    print('DBEUBDUEBEDUBUEDBUED ->', user)

    if user is not None and user.check_password(password):
        login_user(user)

    return redirect(request.referrer)


@core.route('/logout')
def logout():

    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('core.home'))


@core.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('profile-page.html')


@core.route('/register')
def register():
    return render_template('register-page.html')


@core.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    if request.method == 'POST':
        print(request.form)

        for field in Users.editable_fields:
            if field in request.form:
                current_user.__setattr__(field, request.form[field])

        if request.form.get('old_password', '-') == request.form.get('old_password2', '+') and\
                current_user.check_password(request.form['old_password']) and 'new_password' in request.form:
            current_user.set_password(request.form['new_password'])

        current_user.update()

    return render_template('profile-edit.html')



@core.route('/problemlist')
def problemlist():
    return render_template('problems.html')


@core.route('/contestlist')
def contestlist():
    return render_template('contestlist.html')

@core.route('/contestname')
def contest():
    return render_template('contest-page.html')

@core.route('/statement')
def statement():
    return render_template('statement.html')
