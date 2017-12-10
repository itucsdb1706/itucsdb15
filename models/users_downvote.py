import psycopg2 as dbapi2
from flask import current_app


class UsersDownvote:

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS USERS_DOWNVOTE (
                                  user_id       INTEGER REFERENCES USERS(user_id) NOT NULL,
                                  discussion_id INTEGER REFERENCES DISCUSSION(discussion_id) NOT NULL,
                                  PRIMARY KEY (user_id, discussion_id)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def downvote(user_id, discussion_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT user_id, discussion_id FROM USERS_DOWNVOTE
                            WHERE ( user_id = %s AND discussion_id = %s );"""
            cursor.execute(statement, (user_id, discussion_id))
            result = cursor.fetchall()
            cursor.close()

        if result:
            return

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE DISCUSSION SET downvote = downvote + 1 WHERE discussion_id = %s;"""
            cursor.execute(statement, (discussion_id,))
            cursor.close()

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO USERS_DOWNVOTE (user_id, discussion_id) VALUES (%s, %s);"""
            cursor.execute(statement, (user_id, discussion_id))
            cursor.close()
