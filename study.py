from flask import Blueprint
from flask import render_template
from flask import redirect, request, url_for
from flask.helpers import url_for
from flask_login.utils import login_user, current_user, logout_user

from models.team import Team
from models.users import Users
from models.problems import Problems
from models.contest import Contest
from models.submissions import Submissions
from models.discussion import Discussion
from models.users_upvote import UsersUpvote
from models.users_downvote import UsersDownvote
from models.problem_tag import ProblemTag
from models.tag import Tag

from models.contest_user import ContestUser

from utils import login_required, get_submission_score

import urllib.request as url_req

study = Blueprint('study', __name__)


@study.route('/problemlist/')
def problem_list():

    # TODO: This can be mor efficient
    problems = Problems.get_all()
    for problem in problems:
        problem.get_tags()

    if current_user.is_authenticated:
        solved = Submissions.get_solved_problems(current_user)
        tried = Submissions.get_tried_problems(current_user)
    else:
        solved = set()
        tried = set()

    return render_template('problems.html', problems=problems, solved=solved, tried=tried)


@study.route('/contestlist/')
def contest_list():
    contests = Contest.get_all()
    if current_user.is_authenticated:
        registered_contests = current_user.get_registered_contests()
    else:
        registered_contests = set()
    return render_template('contestlist.html', contests=contests, registered_contests=registered_contests)


@study.route('/register_contest/', methods=['POST'])
@login_required
def register_contest():

    contest_id = request.form.get('contest_id', 0)
    contest = Contest.get(contest_id=contest_id)[0]

    if not contest.is_individual and current_user.get_team():
        ContestUser.register_users(contest, current_user.team.get_users())
    else:
        ContestUser.register_users(contest, [current_user])

    return redirect(url_for('study.contest_list'))


@study.route('/user_leaderboard/')
def user_leaderboard():
    users = Users.get_all()
    return render_template('user_leaderboard.html', users=users)


@study.route('/team_leaderboard/')
def team_leaderboard():
    teams = Team.get_all()
    return render_template('team_leaderboard.html', teams=teams)


@study.route('/leaderboard/<string:contest_name>/')
def leaderboard(contest_name):

    contest_dict = Contest.get_with_leaderboard(url_req.unquote(contest_name))

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


@study.route('/contest/<string:contest_name>/')
def contest(contest_name):
    contest = Contest.get_with_problems(contest_name=url_req.unquote(contest_name))[0]
    solved = set()
    tried = set()

    if current_user.is_authenticated:
        solved = Submissions.get_solved_problems(current_user, contest)
        tried = Submissions.get_tried_problems(current_user, contest)

    return render_template('contest-page.html', contest=contest, solved=solved, tried=tried)


@study.route('/statement/<string:problem_id>/', methods=['GET', 'POST'])
def statement(problem_id):

    if request.method == 'GET':
        if current_user.is_authenticated:
            problem = Problems.get_with_submissions(problem_id=problem_id, user_id=current_user.user_id)[0]
        else:
            problem = Problems.get(problem_id=problem_id)[0]

    elif request.method == 'POST':

        if not current_user.is_authenticated:
            return redirect(url_for('core.home'))

        problem = Problems.get_with_submissions(problem_id=problem_id, user_id=current_user.user_id)[0]
        score = get_submission_score(problem.max_score)
        source = request.files['source'].read()
        submission = Submissions(user_id=current_user.user_id, problem_id=problem_id, score=score[0],
                                 is_complete=(score[0] == problem.max_score), language=request.form['language'],
                                 error=score[1])

        max_score = int(Submissions.get_max(current_user.user_id, problem_id))
        increase = score[0]-max_score
        submission.save()

        if increase > 0:
            current_user.increase_rank(increase)
            current_user.get_team()
            if current_user.team is not None:
                current_user.team.increase_rank(increase)

        problem.submissions = [submission] + problem.submissions

    problem.get_sample()
    problem.get_tags()
    problem.get_discussions()
    return render_template('statement.html', problem=problem)


@study.route('/add_discussion/', methods=['POST'])
@login_required
def add_discussion():

    discussion = Discussion(problem_id=request.form['problem_id'], user_id=current_user.user_id,
                            content=request.form['content'])
    discussion.save()
    return redirect(url_for('study.statement', problem_id=request.form['problem_id']))


@study.route('/upvote/', methods=['POST'])
@login_required
def upvote():
    UsersUpvote.upvote(current_user.user_id, request.form['discussion_id'])
    return redirect(request.referrer)


@study.route('/downvote/', methods=['POST'])
@login_required
def downvote():
    UsersDownvote.downvote(current_user.user_id, request.form['discussion_id'])
    return redirect(request.referrer)


@study.route('/tag/<int:tag_id>/')
def tag(tag_id):

    tag = Tag.get(tag_id=tag_id)[0]
    problems = ProblemTag.get_problems_with_tag(tag)

    for i in range(len(problems)):
        problems[i].get_tags()

    return render_template('tag.html', tag=tag, problems=problems)
