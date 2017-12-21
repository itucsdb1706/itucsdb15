from flask import Blueprint
from flask import render_template
from flask import redirect, request, url_for
from flask_login.utils import login_user, current_user, logout_user

from models.message import Message
from models.users import Users
from models.team import Team
from models.tag import Tag

from utils import login_required, is_mail, password_validation, random_string

import os
from datetime import datetime

core = Blueprint('core', __name__)


@core.route('/debug/')
def debug():
    """
    Debug view for dummy pages and debugging.
    :return: HTTP Response
    """
    return render_template('debug.html')


@core.route('/')
def home():
    """
    Home page view.
    :return: HTTP Response
    """
    tags = Tag.get_all()
    return render_template('home.html', tags=tags)


@core.route('/login/', methods=['POST'])
def login():
    """
    Login user view. User token saved into sessions.
    :return: HTTP Response
    """
    email = request.form.get('email', '-')
    password = request.form.get('password', '-')
    user = Users.get(email=email)[0]

    if user is not None and user.check_password(password):
        login_user(user)

    return redirect(request.referrer)


@core.route('/logout/')
def logout():
    """
    Logout user view.
    :return: HTTP Response
    """

    if current_user.is_authenticated:
        logout_user()

    return redirect(url_for('core.home'))


@core.route('/team/<string:team_name>/', methods=['GET'])
def team(team_name):
    """
    Team member list view.
    :param team_name: str
    :return: HTTP Response
    """
    users = Users.get_from_team(team_name=team_name)
    return render_template('user_leaderboard.html', users=users)


@core.route('/profile/<string:username>/', methods=['GET', 'POST'])
def profile(username):
    """
    Profile page view.
    :param username: str
    :return: HTTP Response
    """
    user = Users.get_join(username=username)[0]
    is_owner = current_user.is_authenticated and current_user.user_id == user.user_id
    return render_template('profile-page.html', user=user, is_owner=is_owner)


@core.route('/register/', methods=['GET', 'POST'])
def register():
    """
    User register view.
    :return: HTTP Response
    """

    if request.method == 'GET':
        return render_template('register-page.html')
    else:

        required_inputs = ['username', 'email', 'password1', 'password2', 'terms_and_conditions']
        form_inputs = ['bio', 'country', 'city', 'school']

        for inp in required_inputs:
            if inp not in request.form:
                return redirect(url_for('core.home'))

        if is_mail(request.form['email']) is None or \
                request.form['password1'] != request.form['password2'] or \
                not password_validation(request.form['password1']):
            return redirect(url_for('core.home'))

        user = Users(username=request.form['username'], email=request.form['email'])
        for inp in form_inputs:
            if inp in request.form:
                user.__setattr__(inp, request.form[inp])

        user.save()
        user.set_password(request.form['password1'])
        login_user(user)
        return redirect(url_for('core.home'))


@core.route('/edit-profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Profile editing view.
    :return: HTTP Response
    """

    if request.method == 'POST':

        if 'profile_picture' in request.files and request.files['profile_picture'].filename:
            request.files['profile_picture'].filename = random_string(5) + request.files['profile_picture'].filename
            request.files['profile_picture'].save(os.path.join(os.getcwd(), 'static', 'media', 'profile_pictures',
                                                               request.files['profile_picture'].filename))
            current_user.profile_photo = os.path.join('/static', 'media', 'profile_pictures',
                                                      request.files['profile_picture'].filename)

        for field in Users.editable_fields:
            if field in request.form:
                current_user.__setattr__(field, request.form[field])

        if request.form.get('old_password', '-') == request.form.get('old_password2', '+') and\
                current_user.check_password(request.form['old_password']) and 'new_password' in request.form:
            current_user.set_password(request.form['new_password'])

        current_user.update()

        return redirect(url_for('core.profile', username=current_user.username))

    return render_template('profile-edit.html')


@core.route('/read_msg/', methods=['POST'])
def read_msg():
    """
    Message read view.
    :return: HTTP Response
    """
    message_id = request.form.get('msg_id')
    message = Message.get(message_id=message_id)[0]
    message.update_read()
    return redirect(url_for('core.home'))


@core.route('/send_msg/', methods=['POST'])
def send_msg():
    """
    Sending message view.
    :return: HTTP Response
    """
    to_user_id = request.form.get('to_user', '')
    msg_text = request.form.get('msg_text', '')
    if msg_text != '' and to_user_id != '':
        message = Message(msg_text, False, current_user.user_id, to_user_id, datetime.now())
        message.save()
    return redirect(url_for('core.home'))


@core.route('/join_team/', methods=['POST'])
@login_required
def join_team():
    """
    Joining team view.
    :return: HTTP Response
    """

    team = Team.get(team_name=request.form['team_name'])

    if not team:
        team = Team(team_name=request.form['team_name'])
        team.save()
    else:
        team = team[0]

    current_user.set_team(team.team_id)
    team.increase_rank(current_user.rank)
    return redirect(request.referrer)


@core.route('/leave_team/', methods=['POST'])
@login_required
def leave_team():
    """
    Leaving team view.
    :return: HTTP Response
    """
    current_user.get_team()
    current_user.team.decrease_rank(current_user.rank)
    current_user.leave_team()
    return redirect(request.referrer)
