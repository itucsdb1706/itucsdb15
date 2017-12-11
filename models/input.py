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
            cursor.execute(query, (self.problem_id, self.testcase, self.expected_output))
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
                                  problem_id      INTEGER REFERENCES PROBLEMS(problem_id) ON DELETE CASCADE NOT NULL,
                                  testcase        VARCHAR(1024),
                                  expected_output VARCHAR(1024)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM INPUT WHERE ( {} );""" \
                .format(', '.join(Input.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return [Input.object_converter(row) for row in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT {} FROM INPUT;""".format(', '.join(Input.fields))
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result

    @staticmethod
    def object_converter(values):

        inp = Input('a', 'b', 'c')

        for ind, field in enumerate(Input.fields):
            inp.__setattr__(field, values[ind])

        return inp

    @staticmethod
    def drop():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE  IF EXISTS INPUT CASCADE;"""
            cursor.execute(statement)
            cursor.close()
