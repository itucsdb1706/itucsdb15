from flask import redirect, url_for
from flask_login.utils import current_user

import re
import string
import random
from functools import wraps


def login_required(f):
    """
    A decorator that allows only sites users to reach the given view
    :param f: function
    :return: function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('core.home'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    A decorator that allows only sites admins to reach the given view
    :param f: function
    :return: function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('core.home'))
        return f(*args, **kwargs)
    return decorated_function


def is_mail(email):
    """
    Checks if given mail is valid.
    :param email: str
    :return: re
    """
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def password_validation(password):
    """
    Checks if given password is valid.
    :param password: str
    :return: bool
    """
    return len(password) >= 6 and re.search(r"\d", password)\
           is not None and re.search(r"[a-zA-Z]", password) is not None


def random_string(n):
    """
    Returns a random string lenght of 'n' that can contain only uppercase ASCII character and numbers.
    :param n: int
    :return: str
    """
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def get_submission_score(max_score):
    """
    Gives a score to submission
    :param max_score: int
    :return: tuple
    """

    errors = ['Wrong Answer', 'Compilation Error', 'Runtime Error', 'Memory Limit Exceeded', 'Time Limit Exceeded']
    rand = random.randint(1, 100)

    if rand <= 25:
        return max_score, 'Correct'
    elif rand <= 50:
        return 0, random.choice(errors)

    return random.randint(1, max_score-1), 'OK'
