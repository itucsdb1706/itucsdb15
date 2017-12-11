from flask import Blueprint
from flask import render_template, redirect, request, url_for
from flask import redirect
from flask.helpers import url_for
from flask import current_app

from models.clarification import Clarification
from models.contest import Contest
from models.input import Input
from models.message import Message
from models.notification import Notification
from models.message import Message
from models.problems import Problems
from models.submissions import Submissions
from models.team import Team
from models.users import Users
from models.tag import Tag
from models.notification import Notification

from models.problem_tag import ProblemTag
from models.contest_user import ContestUser
from models.discussion import Discussion
from models.users_upvote import UsersUpvote
from models.users_downvote import UsersDownvote

from utils import admin_required

admin = Blueprint('admin', __name__)


@admin.route('/admin_home/')
@admin_required
def admin_home():
    return render_template('admin_home.html')


@admin.route('/admin_add_contest/', methods=['GET', 'POST'])
@admin_required
def admin_add_contest():

    if request.method == 'POST':
        contest = Contest(contest_name=request.form['contest_name'], is_individual='is_individual' in request.form,
                          start_time=request.form['start_time'], end_time=request.form['end_time'])
        contest.save()

        users = Users.get_all()
        for user in users:
            notification = Notification(notification_id=0, user_id=user.user_id,
                                        content='There is a new contest for you to participate')
            notification.save()
        return redirect(url_for('admin.admin_home'))

    return render_template('admin_add_contest.html')


@admin.route('/admin_add_problem/', methods=['GET', 'POST'])
@admin_required
def admin_add_problem():
    if request.method == 'POST':

        problem = Problems(problem_name=request.form['problem_name'], statement=request.form['statement'],
                           contest_id=request.form['contest_id'], max_score=request.form['max_score'])
        problem.save()

        inp = Input(problem_id=problem.problem_id, testcase=request.form['sample'],
                    expected_output=request.form['sampleout'])
        inp.save()

        for i in range(1, 30):
            if request.form.get('addinp'+str(i), '') and request.form.get('expout'+str(i), ''):
                inp = Input(problem_id=problem.problem_id, testcase=request.form['addinp'+str(i)],
                            expected_output=request.form['expout'+str(i)])
                inp.save()

        tags = []
        for i in range(1, 30):
            if request.form.get('tagin'+str(i), ''):

                tag_name = request.form['tagin'+str(i)]
                tag = Tag.get(tag_name=tag_name)

                if tag:
                    tag = tag[0]
                else:
                    tag = Tag(tag_name=tag_name)
                    tag.save()

                tags.append(tag)

        if tags:
            ProblemTag.save_tags_to_problem(problem, tags)

        return redirect(url_for('admin.admin_home'))
    else:
        contests = Contest.get_all()
        return render_template('admin_add_problem.html', contests=contests)


@admin.route('/admin_send_clarification/', methods=['GET', 'POST'])
@admin_required
def admin_send_clarification():
    if request.method == 'POST':

        contest = Contest.get(contest_id=request.form['contest_id'])[0]
        contest.get_users()

        for user in contest.users:
            clarification = Clarification(contest_id=request.form['contest_id'], user_id=user.user_id,
                                          clarification_content=request.form['content'])
            clarification.save()

        return redirect(url_for('admin.admin_home'))
    else:
        contests = Contest.get_all()
        return render_template('admin_send_clarif.html', contests=contests)
