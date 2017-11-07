import psycopg2 as dbapi2
from flask import current_app


class Submissions:

    def __init__(self, user_id, problem_id, score, is_complete, source, language, error, send_time):
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
            query = """INSERT INTO SUBMISSIONS (user_id, problem_id, score, """\
                    """is_complete, source, language, error, send_time VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, [self.user_id, self.problem_id, self.score,
                                   self.is_complete, self.source, self.language, self.error, self.send_time])
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
            query = """UPDATE SUBMISSIONS SET (user_id, problem_id, score, """\
                    """is_complete, source, language, error, send_time VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, [self.user_id, self.problem_id, self.score,
                                   self.is_complete, self.source, self.language, self.error, self.send_time])
            connection.commit()

    @staticmethod
    def get(input_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM SUBMISSIONS WHERE submission_id=%s"""
            cursor.execute(query, [input_id])
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM SUBMISSIONS """
            cursor.execute(query)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result
