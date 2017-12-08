import psycopg2 as dbapi2
from flask import current_app
from models.users import Users
from models.contest import Contest


class ContestUser:

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS CONTEST_USERS (
                                  contest_id  INTEGER REFERENCES CONTEST(contest_id) NOT NULL,
                                  user_id     INTEGER REFERENCES USERS(user_id) NOT NULL,
                                  PRIMARY KEY (contest_id, user_id)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def register_users(contest, user_list):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO CONTEST_USERS (contest_id, user_id) VALUES (%s, %s);"""
            cursor.executemany(statement, [(contest.contest_id, user.user_id) for user in user_list])
            cursor.close()

    @staticmethod
    def unregister_users(contest, user_list):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM CONTEST_USERS WHERE (contest_id = %s AND user_id = %s);"""
            cursor.executemany(statement, [(contest.contest_id, user.user_id) for user in user_list])
            cursor.close()

    # TODO: Should be implemented in Users?
    '''
    @staticmethod
    def get_registered_contests(user):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM CONTEST NATURAL JOIN CONTEST_USERS WHERE (user_id = %s);""".format()
            cursor.execute(statement, (user.tag_id,))
            problems_as_tuples = cursor.fetchall()
            cursor.close()
            return [Problems(item[1], item[2], item[3], item[4], item[5], item[0]) for item in problems_as_tuples]
    '''