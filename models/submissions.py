import psycopg2 as dbapi2
from flask import current_app
from datetime import datetime
from .users import Users
from .problems import Problems


class Submissions:
    fields = ['submission_id', 'user_id', 'problem_id', 'score', 'is_complete', 'source', 'language', 'error',
              'send_time']

    def __init__(self, user_id, problem_id, score=0, is_complete=False, source='', language='c', error='',
                 send_time=datetime.now()):
        self.user_id = user_id
        self.problem_id = problem_id
        self.score = score
        self.is_complete = is_complete
        self.source = source
        self.language = language
        self.error = error
        self.send_time = send_time

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO SUBMISSIONS (user_id, problem_id, score, is_complete, source, language, error,
                        send_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING submission_id;"""
            cursor.execute(query, (self.user_id, self.problem_id, self.score,
                                   self.is_complete, self.source, self.language, self.error, self.send_time))
            self.submission_id = cursor.fetchone()[0]
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM SUBMISSIONS WHERE submission=%s"""
            cursor.execute(query, [self.submission_id])
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE SUBMISSIONS SET user_id = %s, problem_id = %s, score = %s, is_complete = %s, source = %s,
                        language = %s, error = %s, send_time = %s WHERE submission_id = %s;"""
            cursor.execute(query, (self.user_id, self.problem_id, self.score, self.is_complete,self.source,
                                   self.language, self.error, self.send_time, self.submission_id))
            connection.commit()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS SUBMISSIONS (
                                              submission_id SERIAL PRIMARY KEY NOT NULL,
                                              user_id       INTEGER REFERENCES USERS(user_id) NOT NULL,
                                              problem_id    INTEGER REFERENCES PROBLEMS(problem_id) NOT NULL,
                                              score         INT NOT NULL,
                                              is_complete   BOOLEAN NOT NULL,
                                              source        VARCHAR(1024),
                                              language      VARCHAR(10),
                                              error         VARCHAR(100),
                                              send_time     TIMESTAMP NOT NULL 
                                              );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM SUBMISSIONS WHERE ( {} );"""\
                .format(', '.join(Submissions.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            cursor.execute(statement)
            result = cursor.fetchall()
            connection.commit()
            return [Submissions.object_converter(row) for row in result]

    @staticmethod
    def get_solved_problems(user, contest=None):
        if contest is not None:
            with dbapi2.connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT PROBLEMS.problem_id FROM PROBLEMS 
                INNER JOIN SUBMISSIONS ON (PROBLEMS.problem_id = SUBMISSIONS.problem_id)
                WHERE ( PROBLEMS.contest_id = %s AND SUBMISSIONS.user_id = %s AND SUBMISSIONS.is_complete = TRUE );"""\
                    .format(', '.join(Submissions.fields))
                print(statement)
                cursor.execute(statement, (contest.contest_id, user.user_id))
                result = cursor.fetchall()
                cursor.close()
        else:
            with dbapi2.connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT PROBLEMS.problem_id FROM PROBLEMS 
                      INNER JOIN SUBMISSIONS ON (PROBLEMS.problem_id = SUBMISSIONS.problem_id)
                      WHERE ( SUBMISSIONS.user_id = %s AND SUBMISSIONS.is_complete = TRUE );"""\
                    .format(', '.join(Submissions.fields))
                cursor.execute(statement, (user.user_id,))
                result = cursor.fetchall()
                cursor.close()

        solved_set = set()
        for row in result:
            solved_set.add(row[0])

        return solved_set

    @staticmethod
    def get_tried_problems(user, contest=None):
        if contest is not None:
            with dbapi2.connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT PROBLEMS.problem_id FROM PROBLEMS 
                INNER JOIN SUBMISSIONS ON (PROBLEMS.problem_id = SUBMISSIONS.problem_id)
                WHERE ( PROBLEMS.contest_id = %s AND SUBMISSIONS.user_id = %s AND SUBMISSIONS.is_complete = FALSE );"""\
                    .format(', '.join(Submissions.fields))
                cursor.execute(statement, (contest.contest_id, user.user_id))
                result = cursor.fetchall()
                cursor.close()
        else:
            with dbapi2.connect(current_app.config['dsn']) as connection:
                cursor = connection.cursor()
                statement = """SELECT PROBLEMS.problem_id FROM PROBLEMS 
                          INNER JOIN SUBMISSIONS ON (PROBLEMS.problem_id = SUBMISSIONS.problem_id)
                          WHERE ( SUBMISSIONS.user_id = %s AND SUBMISSIONS.is_complete = FALSE );""" \
                    .format(', '.join(Submissions.fields))
                cursor.execute(statement, (user.user_id,))
                result = cursor.fetchall()
                cursor.close()

        solved_set = set()
        for row in result:
            solved_set.add(row[0])

        return solved_set

    @staticmethod
    def get_join(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {}, {}, {} FROM SUBMISSIONS INNER JOIN USERS ON (SUBMISSIONS.user_id = USERS.user_id)
                                              INNER JOIN PROBLEMS ON (SUBMISSIONS.problem_id = PROBLEMS.problem_id)
                                              WHERE ( {} );"""\
                .format(', '.join(map(lambda x: 'SUBMISSIONS.' + x, Submissions.fields)),
                        ', '.join(map(lambda x: 'USERS.' + x, Users.fields)),
                        ', '.join(map(lambda x: 'PROBLEMS.' + x, Problems.fields)),
                        'AND '.join(['USERS.' + key + ' = %s' for key in kwargs]))
            print(statement)
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            print(result)
            cursor.close()
            return [Submissions.object_converter(row, True) for row in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT {} FROM SUBMISSIONS;""".format(', '.join(Submissions.fields))
            cursor.execute(query)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def object_converter(values, is_joined=False):

        submission = Submissions('a', 'b')

        for ind, field in enumerate(Submissions.fields):
            submission.__setattr__(field, values[ind])

        if is_joined:

            user = Users('a', 'b')

            for ind, field in enumerate(Users.fields):
                submission.__setattr__(field, values[len(Submissions.fields) + ind])

            submission.user = user

            problem = Problems('a', 'b')

            for ind, field in enumerate(Problems.fields):
                submission.__setattr__(field, values[len(Submissions.fields) + len(Users.fields) + ind])

            submission.problem = problem

        return submission
