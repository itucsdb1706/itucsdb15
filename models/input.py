import psycopg2 as dbapi2
from flask import current_app


class Input:

    def __init__(self, problem_id, testcase, expected_output):
        self.problem_id = problem_id
        self.testcase = testcase
        self.expected_output = expected_output

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO INPUT (problem_id, testcase, expected_output) VALUES (%s, %s, %s)"""
            cursor.execute(query, [self.problem_id, self.testcase, self.expected_output])
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM INPUT WHERE input_id=%s"""
            cursor.execute(query, [self.input_id])
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE INPUT SET (problem_id, testcase, expected_output) WHERE input_id=%s VALUES (%s, %s, %s)"""
            cursor.execute(query, [self.input_id, self.problem_id, self.testcase, self.expected_output])
            connection.commit()

    @staticmethod
    def get(input_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM INPUT WHERE input_id=%s"""
            cursor.execute(query, [input_id])
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM INPUT """
            cursor.execute(query)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result
