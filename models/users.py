import psycopg2 as dbapi2
from flask import current_app
from datetime import datetime
from flask_login import UserMixin
from passlib.apps import custom_app_context as pwd_context


class Users(UserMixin):
    fields = ['user_id', 'username', 'email', 'password', 'rank', 'team_id', 'profile_photo', 'school', 'city',
              'country', 'bio']

    def __init__(self, username, email, password, rank=0, team_id=None, profile_photo=None, school=None, city=None,
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
            statement = """DELETE FROM USERS 
                                      WHERE (user_id = %s);"""
            cursor.execute(statement, (self.user_id,))
            cursor.close()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE USERS
                                  SET email = %s, rank = %s, team_id = %s, profile_photo = %s, school = %s, city = %s,
                                  country = %s, bio = %s
                                  WHERE (user_id = %s);"""
            cursor.execute(statement, (self.email,
                                       self.rank,
                                       self.team_id,
                                       self.profile_photo,
                                       self.school,
                                       self.city,
                                       self.county,
                                       self.bio,
                                       self.user_id))
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

    def get_id(self):
        return self.user_id

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS USERS (
                                      user_id       SERIAL PRIMARY KEY NOT NULL,
                                      username      VARCHAR(32),
                                      email         VARCHAR(100),
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
    def get(user_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM USERS
                                      WHERE (user_id = %s);"""
            cursor.execute(statement, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            return Users.user_object(result)

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM USERS;"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return result

    @staticmethod
    def user_object(values):

        user = Users('a', 'b', 'c')

        for ind, field in enumerate(Users.fields):
            user.__setattr__(field, values[ind])

        return user


