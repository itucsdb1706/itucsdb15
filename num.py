from flask import Blueprint
from flask import render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app

num = Blueprint('num', __name__)


@num.route('/number_checker/<int:number>')
def check_number(number):
    """
    If given number is less than 10, prints the number; else redirects to home page
    """
    if number >= 10:
        return redirect(url_for('core.home'))
    return render_template('number.html', number=number)
