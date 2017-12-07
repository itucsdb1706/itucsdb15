from flask import redirect, url_for
from functools import wraps
from flask_login.utils import current_user
import re


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('core.home'))
        return f(*args, **kwargs)
    return decorated_function


def is_mail(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def password_validation(password):
    return len(password) >= 6 and re.search(r"\d", password)\
           is not None and re.search(r"[a-zA-Z]", password) is not None
