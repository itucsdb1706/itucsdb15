import psycopg2 as dbapi2
from flask import current_app


class Input:
    fields = ['input_id', 'problem_id', 'testcase', 'expected_output']

    def __init__(self, problem_id, testcase, expected_output):
        self.problem_id = problem_id
        self.testcase = testcase
        self.expected_output = expected_output

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO INPUT (problem_id, testcase, expected_output) VALUES (%s, %s, %s)
                        RETURNING input_id;"""
            cursor.execute(query, [self.problem_id, self.testcase, self.expected_output])
            self.input_id = cursor.fetchone()[0]
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM INPUT WHERE input_id = %s;"""
            cursor.execute(query, self.input_id)
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE INPUT SET problem_id = %s, testcase = %s, expected_output = %s WHERE input_id=%s;"""
            cursor.execute(query, (self.problem_id, self.testcase, self.expected_output, self.input_id))
            connection.commit()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS INPUT (
                                  input_id        SERIAL PRIMARY KEY NOT NULL,
                                  problem_id      INTEGER REFERENCES PROBLEMS(problem_id) NOT NULL,
                                  testcase        VARCHAR(1024),
                                  expected_output VARCHAR(1024)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(*args, **kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM USERS
                                    WHERE (""" + ' '.join([key + ' = ' + str(kwargs[key]) for key in kwargs]) + """);"""
            cursor.execute(statement)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM INPUT;"""
            cursor.execute(query)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def object_converter(values):

        input = Input('a', 'b', 'c')

        for ind, field in enumerate(Input.fields):
            input.__setattr__(field, values[ind])

        return input
