from flask import Blueprint
from flask import render_template
from flask import redirect, request, url_for
from flask.helpers import url_for
from flask import request
from flask_login.utils import login_user, current_user, logout_user

from models.users import Users
from models.problems import Problems
from models.contest import Contest
from models.submissions import Submissions

from models.contest_user import ContestUser

from utils import login_required

study = Blueprint('study', __name__)


@study.route('/problemlist')
def problem_list():

    problems = Problems.get_all()

    if current_user.is_authenticated:
        solved = Submissions.get_solved_problems(current_user)
        tried = Submissions.get_tried_problems(current_user)
    else:
        solved = set()
        tried = set()

    return render_template('problems.html', problems=problems, solved=solved, tried=tried)


@study.route('/contestlist')
def contest_list():
    contests = Contest.get_all()
    if current_user.is_authenticated:
        registered_contests = current_user.get_registered_contests()
    else:
        registered_contests = set()
    return render_template('contestlist.html', contests=contests, registered_contests=registered_contests)


@study.route('/register_contest', methods=['POST'])
@login_required
def register_contest():

    contest_id = request.form.get('contest_id', 0)
    contest = Contest.get(contest_id=contest_id)[0]

    if not contest.is_individual and current_user.get_team():
        ContestUser.register_users(contest, current_user.team.get_users())
    else:
        ContestUser.register_users(contest, [current_user])

    return redirect(url_for('study.contest_list'))


@study.route('/leaderboard/<string:contest_name>')
def leaderboard(contest_name):

    contest_dict = Contest.get_with_leaderboard(contest_name)

    contest = contest_dict['contest']
    contest.get_problems()

    users = [contest_dict['users'][key] for key in contest_dict['users']]

    for user in users:
        user.score = sum(map(lambda problem: problem.score, user.problems))
        user.solved = set()
        user.tried = set()
        for problem in user.problems:
            if problem.is_complete:
                user.solved.add(problem.problem_id)
            else:
                user.tried.add(problem.problem_id)

    users.sort(key=lambda user: -user.score)

    return render_template('leaderboard.html', contest=contest, users=users)


@study.route('/contest/<string:contest_name>')
def contest(contest_name):

    contest = Contest.get_with_problems(contest_name=contest_name)[0]
    solved = set()
    tried = set()

    if current_user.is_authenticated:
        solved = Submissions.get_solved_problems(current_user, contest)
        tried = Submissions.get_tried_problems(current_user, contest)

    return render_template('contest-page.html', contest=contest, solved=solved, tried=tried)


# TODO: discussion and post
@study.route('/statement/<string:problem_id>', methods=['GET', 'POST'])
def statement(problem_id):

    if request.method == 'GET':
        if current_user.is_authenticated:
            problem = Problems.get_with_submissions(problem_id=problem_id, user_id=current_user.user_id)[0]
        else:
            problem = Problems.get(problem_id=problem_id)
        problem.get_sample()

    return render_template('statement.html', problem=problem)
