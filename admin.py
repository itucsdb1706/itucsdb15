from flask import Blueprint
from flask import render_template, redirect, request, url_for
from flask import redirect
from flask.helpers import url_for
from flask import current_app

from models.clarification import Clarification
from models.contest import Contest
from models.input import Input
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
from datetime import datetime, timedelta

import os

admin = Blueprint('admin', __name__)


@admin.route('/admin_home/')
@admin_required
def admin_home():
    return render_template('admin_home.html')


@admin.route('/init_db/')
def init_db():

    if not os.path.exists(os.path.join(os.getcwd(), 'static', 'media')):
        os.makedirs(os.path.join(os.getcwd(), 'static', 'media'))
        os.mkdir(os.path.join(os.getcwd(), 'static', 'media', 'profile_pictures'))

    Team.create()
    Users.create()

    if len(Users.get(is_admin=True)) == 0:

        tables = [Team, Contest, Users, Problems, Tag, ProblemTag, Message, Clarification, Notification, Discussion,
                  Submissions, Input, ContestUser, UsersUpvote, UsersDownvote]

        for table in tables[::-1]:
            table.drop()
        for table in tables:
            table.create()

        # Teams and Users
        bumbles = Team(team_name='HumbleBumbles')
        bumbles.save()
        burakbugrul = Users(username='burakbugrul', email='bbugrul96@gmail.com', password='123456gs', is_admin=True,
                            team_id=bumbles.team_id)
        burakbugrul.save()

        packers = Team(team_name='HackerPackers')
        packers.save()
        hackergirl = Users(username='hackergirl123', email='info@hackpack.com', password='123456gs', is_admin=True,
                           team_id=packers.team_id)
        hackergirl.save()
        pax = Users(username='pax', email='pax@pax.com', password='123456gs', is_admin=True, team_id=packers.team_id)
        pax.save()

        # Contests
        online = Contest(contest_name='online', start_time=datetime.now(),
                         end_time=datetime.now()+timedelta(days=1000))
        online.save()

        past = Contest(contest_name='past', start_time=datetime.now() - timedelta(days=1000),
                       end_time=datetime.now() - timedelta(days=1))
        past.save()

        future = Contest(contest_name='future', start_time=datetime.now()+timedelta(days=500),
                         end_time=datetime.now() + timedelta(days=1000))
        future.save()

        # Problems
        easy = Problems(problem_name='Easy', statement='This problem is easy', contest_id=online.contest_id,
                        max_score=100)
        easy.save()

        moderate = Problems(problem_name='Moderate', statement='This problem is moderate', contest_id=online.contest_id,
                            max_score=100)
        moderate.save()

        hard = Problems(problem_name='Hard', statement='This problem is hard', contest_id=online.contest_id,
                        max_score=100)
        hard.save()

        past_prob = Problems(problem_name='Old', statement='This problem is old', contest_id=past.contest_id,
                             max_score=100)
        past_prob.save()

        new_prob = Problems(problem_name='New', statement='This problem is new', contest_id=future.contest_id,
                            max_score=100)
        new_prob.save()

        # Tags

        dynamic = Tag(tag_name='Dynamic')
        dynamic.save()

        graph = Tag(tag_name='Graph')
        graph.save()

        greedy = Tag(tag_name='Greedy')
        greedy.save()

        games = Tag(tag_name='Game-Theory')
        games.save()

        ProblemTag.save_tags_to_problem(easy, [greedy])
        ProblemTag.save_tags_to_problem(moderate, [dynamic, games])
        ProblemTag.save_tags_to_problem(hard, [dynamic, graph, greedy])

        # Inputs

        inp = Input(problem_id=easy.problem_id, testcase='input', expected_output='output')
        inp.save()

        inp = Input(problem_id=easy.problem_id, testcase='input2', expected_output='output2')
        inp.save()

        inp = Input(problem_id=moderate.problem_id, testcase='input moderate', expected_output='output moderate')
        inp.save()

        inp = Input(problem_id=hard.problem_id, testcase='input hard', expected_output='output hard')
        inp.save()

    return redirect(url_for('core.home'))


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
