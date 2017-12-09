import psycopg2 as dbapi2
from flask import current_app
from datetime import datetime


class Discussion:
    fields = ['discussion_id', 'problem_id', 'user_id', 'content', 'post_time', 'upvote', 'downvote']

    def __init__(self, discussion_id, problem_id, user_id, content, post_time = datetime.now() , upvote = 0, downvote = 0):
        self.discussion_id = discussion_id
        self.problem_id = problem_id
        self.user_id = user_id
        self.content= content
        self.post_time = post_time
        self.upvote = upvote
        self.downvote = downvote

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO DISCUSSION ( problem_id, user_id, content, post_time, upvote, downvote) VALUES ( %s, %s, %s, %s, %s, %s)
                        RETURNING discussion_id;"""
            cursor.execute(query, [self.problem_id, self.user_id, self.content, self.post_time, self.upvote, self.downvote])
            self.discussion_id = cursor.fetchone()[0]
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM DISCUSSION WHERE discussion_id = %s;"""
            cursor.execute(query, self.discussion_id)
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE INPUT SET  upvote = %s, downvote = %s WHERE discussion_id=%s;"""
            cursor.execute(query, (self.upvote, self.downvote, self.discussion_id))
            connection.commit()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS DISCUSSION (
                                    discussion_id   SERIAL PRIMARY KEY NOT NULL,
                                    problem_id      INTEGER REFERENCES PROBLEMS(problem_id) NOT NULL,
                                    user_id         INTEGER REFERENCES USERS(user_id) NOT NULL,
                                    content         VARCHAR(500),
                                    post_time       TIMESTAMP NOT NULL,
                                    upvote          INTEGER NOT NULL,
                                    downvote        INTEGER NOT NULL
                                    );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM INPUT WHERE ( {} );""" \
                .format(', '.join(Discussion.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            cursor.execute(statement)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return [Discussion.object_converter(row) for row in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT {} FROM DISCUSSION;""".format(', '.join(Discussion.fields))
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result

    @staticmethod
    def object_converter(values):

        disc = Discussion('a', 'b', 'c', 'd', datetime.now(), 0, 0)

        for ind, field in enumerate(Discussion.fields):
            disc.__setattr__(field, values[ind])

        return disc
