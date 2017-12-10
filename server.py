from flask import Flask
from flask_login import LoginManager

from core import core
from models.clarification import Clarification
from num import num
from study import study
from admin import admin

from models.users import Users
from models.message import Message
from models.notification import Notification

import os
import json
import re


lm = LoginManager()


# ElephantSQL JSON parser for the DSN string
def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


@lm.user_loader
def load_user(user_id):
    user = None
    print('asasd->', Notification.get(user_id=user_id))
    try:
        user = Users.get(user_id=user_id)[0]
        user.msg_list = Message.get_messages_for_user(user)

        user.other_users = [(ouser.user_id, ouser.username)
                            for ouser in Users.get_all()
                            if user.user_id != ouser.user_id]
        
        user.notifications = Notification.get(user_id=user.user_id)
        print('AAAAAAAAAA->', user.notifications)

        user.clarifications = Clarification.get_clarifications_for_user(user)
    finally:
        return user


def create_app():
    app = Flask(__name__)
    app.secret_key = 'suchsecretmuchwow'
    app.config.from_object('settings')
    app.register_blueprint(core)
    app.register_blueprint(study)
    app.register_blueprint(num)
    app.register_blueprint(admin)

    lm.init_app(app)
    lm.login_view = 'core.login_page'
    return app


def main():
    app = create_app()
    port = app.config.get('PORT', 5000)

    # Required code for ElephantSQL
    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        app.config['dsn'] = """user='vagrant' password='vagrant'
                               host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
