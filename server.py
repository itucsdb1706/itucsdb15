import datetime
import os

from flask import Flask
from flask import redirect
from flask import render_template
from flask.helpers import url_for


app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
# TODO: Django like app partition


@app.route('/')
def home_page():
    now = datetime.datetime.now()
    return render_template('home.html', current_time=now.ctime(), tmp_list=[1, 2, 3, 4], tmp_if=3)


@app.route('/number_checker/<int:number>')
def check_number(number):
    """
    If given number is less than 10, prints the number; else redirects to home page
    """
    if number >= 10:
        return redirect(url_for('home_page'))
    return render_template('number.html', number=number)


if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)
