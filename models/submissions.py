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
            query = """INSERT INTO SUBMISSIONS (user_id, problem_id, score, is_complete, source, language, error,
                        send_time VALUES (%s, %s, %s, %s, %s) RETURNING submission_id;"""
            cursor.execute(query, [self.user_id, self.problem_id, self.score,
                                   self.is_complete, self.source, self.language, self.error, self.send_time])
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
    def get(submission_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM SUBMISSIONS WHERE submission_id=%s;"""
            cursor.execute(query, (submission_id))
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM SUBMISSIONS;"""
            cursor.execute(query)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result
