from flask import redirect, url_for
from functools import wraps
from flask_login.utils import current_user


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('core.home'))
        return f(*args, **kwargs)
    return decorated_function
