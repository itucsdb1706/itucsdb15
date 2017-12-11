import psycopg2 as dbapi2
from flask import current_app


class UsersUpvote:

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS USERS_UPVOTE (
                                  user_id       INTEGER REFERENCES USERS(user_id) NOT NULL,
                                  discussion_id INTEGER REFERENCES DISCUSSION(discussion_id) NOT NULL,
                                  PRIMARY KEY (user_id, discussion_id)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def upvote(user_id, discussion_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT user_id, discussion_id FROM USERS_UPVOTE
                            WHERE ( user_id = %s AND discussion_id = %s );"""
            cursor.execute(statement, (user_id, discussion_id))
            result = cursor.fetchall()
            cursor.close()

        if result:
            return

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE DISCUSSION SET upvote = upvote + 1 WHERE discussion_id = %s;"""
            cursor.execute(statement, (discussion_id,))
            cursor.close()

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO USERS_UPVOTE (user_id, discussion_id) VALUES (%s, %s);"""
            cursor.execute(statement, (user_id, discussion_id))
            cursor.close()

    @staticmethod
    def drop():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE  IF EXISTS USERS_UPVOTE;"""
            cursor.execute(statement)
            cursor.close()