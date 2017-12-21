import psycopg2 as dbapi2
from flask import current_app
from datetime import datetime


class Discussion:
    fields = ['discussion_id', 'problem_id', 'user_id', 'content', 'post_time', 'upvote', 'downvote']

    def __init__(self, problem_id, user_id, content, post_time=datetime.now(), upvote=0, downvote=0):
        self.problem_id = problem_id
        self.user_id = user_id
        self.content = content
        self.post_time = post_time
        self.upvote = upvote
        self.downvote = downvote

    def save(self):
        """
        Inserts discussion into database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO DISCUSSION ( problem_id, user_id, content, post_time, upvote, downvote)
                        VALUES ( %s, %s, %s, %s, %s, %s) RETURNING discussion_id;"""
            cursor.execute(query, [self.problem_id, self.user_id, self.content, self.post_time, self.upvote,
                                   self.downvote])
            self.discussion_id = cursor.fetchone()[0]
            connection.commit()

    def delete(self):
        """
        Deletes discussion from database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM DISCUSSION WHERE discussion_id = %s;"""
            cursor.execute(query, self.discussion_id)
            connection.commit()

    def update(self):
        """
        Updates discussion in database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE INPUT SET  upvote = %s, downvote = %s WHERE discussion_id = %s;"""
            cursor.execute(query, (self.upvote, self.downvote, self.discussion_id))
            connection.commit()

    @staticmethod
    def create():
        """
        Creates DISCUSSION table in database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS DISCUSSION (
                                    discussion_id   SERIAL PRIMARY KEY NOT NULL,
                                    problem_id      INTEGER REFERENCES PROBLEMS(problem_id) ON DELETE CASCADE NOT NULL,
                                    user_id         INTEGER REFERENCES USERS(user_id) ON DELETE CASCADE NOT NULL,
                                    content         VARCHAR(500),
                                    post_time       TIMESTAMP NOT NULL,
                                    upvote          INTEGER NOT NULL,
                                    downvote        INTEGER NOT NULL
                                    );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        """
        Queries discussions from database according to given arguments.
        :param kwargs: Arguments
        :return: list
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM DISCUSSION WHERE ( {} ) ORDER BY discussion_id;""" \
                .format(', '.join(Discussion.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return [Discussion.object_converter(row) for row in result]

    @staticmethod
    def get_all():
        """
        Gets all discussions from database.
        :return: list
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT {} FROM DISCUSSION;""".format(', '.join(Discussion.fields))
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result

    @staticmethod
    def object_converter(values):
        """
        Creates a Discussion object with given arguments.
        :param values: Objects attributes(tuple)
        :return: None
        """

        disc = Discussion('a', 'b', 'c')

        for ind, field in enumerate(Discussion.fields):
            disc.__setattr__(field, values[ind])

        return disc

    @staticmethod
    def drop():
        """
        Drops DISCUSSION table.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE  IF EXISTS DISCUSSION CASCADE;"""
            cursor.execute(statement)
            cursor.close()
