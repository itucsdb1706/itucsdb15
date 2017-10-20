from flask import Blueprint
from flask import render_template
from flask import redirect
from flask.helpers import url_for
from flask import current_app
from flask import request

core = Blueprint('core', __name__)


@core.route('/')
def home():
    return render_template('home.html')
