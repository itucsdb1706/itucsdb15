import psycopg2 as dbapi2
from flask import current_app


class Problems:

    def __init__(self, problem_name, statement, contest_id, max_score, editorial):
        self.problem_name = problem_name
        self.statement = statement
        self.contest_id = contest_id
        self.max_score = max_score
        self.editorial = editorial

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO PROBLEMS (problem_name, statement, contest_id, max_score, editorial)""" \
                    + """VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, [self.problem_name, self.statement, self.contest_id, self.max_score, self.editorial])
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM PROBLEMS WHERE problem_id=%s"""
            cursor.execute(query, [self.problem_id])
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE PROBLEMS SET (problem_name, statement, contest_id, max_score, editorial)""" \
                    + """VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, [self.problem_name, self.statement, self.contest_id, self.max_score, self.editorial])
            connection.commit()

    @staticmethod
    def get(problem_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM PROBLEMS WHERE problem_id=%s"""
            cursor.execute(query, [problem_id])
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM PROBLEMS"""
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result