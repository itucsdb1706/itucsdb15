from flask import Blueprint
from flask import render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app

from models.clarification import Clarification
from models.comment import Comment
from models.contest import Contest
from models.input import Input
# from models.message import Message
# from models.notification import Notification
from models.message import Message
from models.problems import Problems
from models.submissions import Submissions
from models.team import Team
from models.users import Users
from models.tag import Tag

from models.problem_tag import ProblemTag
from models.contest_user import ContestUser


num = Blueprint('num', __name__)


@num.route('/number_checker/<int:number>')
def check_number(number):
    """
    If given number is less than 10, prints the number; else redirects to home page
    """

    Team.create()
    Users.create()
    Contest.create()

    Clarification.create()
    Problems.create()
    Input.create()
    Submissions.create()
    Message.create()
    # Tag.create()

    ContestUser.create()
    # ProblemTag.create()

    # u = Users(username='burakbugrul', email='bbugrul96@gmail.com', password='123456gs')
    # u.save()

    if number >= 10:
        return redirect(url_for('core.home'))
    return render_template('number.html', number=number)
