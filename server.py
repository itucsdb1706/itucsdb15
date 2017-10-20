from flask import Flask
from flask_login import LoginManager

from core import core
from num import num
from user import get_user
from problem import Problem


lm = LoginManager()


@lm.user_loader
def load_user(user_id):
    return get_user(user_id)


def create_app():
    app = Flask(__name__)
    app.config.from_object('settings')
    app.register_blueprint(core)
    app.register_blueprint(num)

    lm.init_app(app)
    lm.login_view = 'core.login_page'
    return app


def main():
    app = create_app()
    port = app.config.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
