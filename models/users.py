import psycopg2 as dbapi2
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context
from .team import Team
from .contest import Contest


class Users(UserMixin):
    fields = ['user_id', 'username', 'email', 'password', 'rank', 'team_id', 'profile_photo', 'school', 'city',
              'country', 'bio']
    editable_fields = ['email', 'bio', 'country', 'city', 'school', 'profile_photo']

    def __init__(self, username, email, password='', rank=0, team_id=None, profile_photo=None, school=None, city=None,
                 country=None, bio=None):
        self.username = username
        self.email = email
        self.password = pwd_context.encrypt(password)
        self.rank = rank
        self.register_date = datetime.now()
        self.team_id = team_id
        self.profile_photo = profile_photo
        self.school = school
        self.city = city
        self.country = country
        self.bio = bio

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO USERS ( username, email, password, rank, register_date, team_id, profile_photo,
                            school, city, country, bio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING user_id;"""
            cursor.execute(statement, (self.username, self.email, self.password, self.rank, self.register_date,\
                                       self.team_id, self.profile_photo, self.school, self.city, self.country,\
                                       self.bio))
            self.user_id = cursor.fetchone()[0]
            cursor.close()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM USERS WHERE (user_id = %s);"""
            cursor.execute(statement, (self.user_id,))
            cursor.close()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            set_condition = ', '.join([field + '= %s' for field in Users.editable_fields])
            statement = """UPDATE USERS SET {} WHERE (user_id = %s);""".format(set_condition)
            print(statement)
            print(tuple(str(self.__getattribute__(field)) for field in Users.editable_fields)
                  + (str(self.user_id),))
            cursor.execute(statement, tuple(str(self.__getattribute__(field)) for field in Users.editable_fields)\
                           + (str(self.user_id),))
            cursor.close()

    def set_password(self, password):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            hashed = pwd_context.encrypt(password)
            statement = """UPDATE USERS SET password = %s WHERE (user_id = %s);"""
            cursor.execute(statement, (hashed, self.user_id))
            cursor.close()

    def check_password(self, password):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT password FROM USERS WHERE (user_id = %s);"""
            cursor.execute(statement, (self.user_id,))
            return_value = pwd_context.verify(password, cursor.fetchone()[0])
            cursor.close()
        return return_value

    def get_team(self):
        self.team = Team.get(team_id=self.team_id)
        return self.team

    def get_submissions(self):
        from .submissions import Submissions
        self.submissions = Submissions.get_join(user_id=self.user_id)

    def get_notifications(self):
        pass

    def get_registered_contests(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT contest_id FROM CONTEST NATURAL JOIN CONTEST_USERS WHERE (user_id = %s);"""
            cursor.execute(statement, (self.user_id,))
            result = cursor.fetchall()
            cursor.close()
            contest_set = set()
            for row in result:
                contest_set.add(row[0])
            return contest_set

    def get_id(self):
        return self.user_id

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS USERS (
                                      user_id       SERIAL PRIMARY KEY NOT NULL,
                                      username      VARCHAR(32) UNIQUE,
                                      email         VARCHAR(100) UNIQUE,
                                      password      VARCHAR(256),
                                      rank          INT NOT NULL,
                                      register_date TIMESTAMP NOT NULL,
                                      team_id       INTEGER REFERENCES TEAM(team_id),
                                      profile_photo VARCHAR(4096),
                                      school        VARCHAR(140),
                                      city          VARCHAR(140),
                                      country       VARCHAR(140),
                                      bio           VARCHAR(512)
                                      );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM USERS WHERE ( {} );"""\
                .format(', '.join(Users.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            print(statement)
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            cursor.close()
            return [Users.object_converter(row) for row in result]

    @staticmethod
    def get_join(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {}, {} FROM USERS INNER JOIN TEAM ON (USERS.team_id = TEAM.team_id) WHERE ( {} );""" \
                .format(', '.join(map(lambda x: 'USERS.' + x, Users.fields)),
                        ', '.join(map(lambda x: 'TEAM.' + x, Team.fields)),
                        'AND '.join(['USERS.' + key + ' = %s' for key in kwargs]))
            print(statement)
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            print(result)
            cursor.close()
            return [Users.object_converter(row, ['TEAM']) for row in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM USERS;""".format(', '.join(Users.fields))
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return [Users.object_converter(row) for row in result]

    @staticmethod
    def object_converter(values, is_joined=False):

        user = Users('a', 'b', 'c')

        for ind, field in enumerate(Users.fields):
            user.__setattr__(field, values[ind])

        if is_joined:
            team = Team('a')
            for ind, field in enumerate(Team.fields):
                team.__setattr__(field, values[len(Users.fields)+ind])
            user.team = team

        return user
