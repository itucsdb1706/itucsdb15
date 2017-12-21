import psycopg2 as dbapi2
from flask import current_app
from models.users import Users
from models.contest import Contest


class ContestUser:

    @staticmethod
    def create():
        """
        Creates CONTEST_USERS table in database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS CONTEST_USERS (
                                  contest_id  INTEGER REFERENCES CONTEST(contest_id) ON DELETE CASCADE NOT NULL,
                                  user_id     INTEGER REFERENCES USERS(user_id) ON DELETE CASCADE NOT NULL,
                                  PRIMARY KEY (contest_id, user_id)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def register_users(contest, user_list):
        """
        Registers a list of users to given contest
        :param contest: Contest object
        :param user_list: Users list
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO CONTEST_USERS (contest_id, user_id) VALUES (%s, %s);"""
            cursor.executemany(statement, [(contest.contest_id, user.user_id) for user in user_list])
            cursor.close()

    @staticmethod
    def unregister_users(contest, user_list):
        """
        Unregisters a list of users to given contest
        :param contest: Contest object
        :param user_list: Users list
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM CONTEST_USERS WHERE (contest_id = %s AND user_id = %s);"""
            cursor.executemany(statement, [(contest.contest_id, user.user_id) for user in user_list])
            cursor.close()

    @staticmethod
    def drop():
        """
        Drops CONTEST_USERS table.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE  IF EXISTS CONTEST_USERS CASCADE;"""
            cursor.execute(statement)
            cursor.close()