import psycopg2 as dbapi2
from flask import current_app


class Problems:
    fields = ['problem_id', 'problem_name', 'statement', 'contest_id', 'max_score', 'editorial']

    def __init__(self, problem_name, statement, contest_id=None, max_score=0, editorial=None, problem_id=None):
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.statement = statement
        self.contest_id = contest_id
        self.max_score = max_score
        self.editorial = editorial

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO PROBLEMS (problem_name, statement, contest_id, max_score, editorial)""" \
                    + """VALUES (%s, %s, %s, %s, %s) RETURNING problem_id;"""
            cursor.execute(query, [self.problem_name, self.statement, self.contest_id, self.max_score, self.editorial])
            self.problem_id = cursor.fetchone()[0]
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM PROBLEMS WHERE problem_id = %s;"""
            cursor.execute(query, [self.problem_id])
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE PROBLEMS SET problem_name = %s, statement = %s, contest_id = %s, 
                        max_score = %s, editorial = %s WHERE problem_id=%s;"""
            cursor.execute(query, (self.problem_name, self.statement, self.contest_id, self.max_score,
                                   self.editorial, self.problem_id))
            connection.commit()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS PROBLEMS (
                                      problem_id    SERIAL PRIMARY KEY NOT NULL,
                                      problem_name  VARCHAR(140),
                                      statement     VARCHAR(1000),
                                      contest_id    INTEGER REFERENCES CONTEST(contest_id) NOT NULL,
                                      max_score     INT NOT NULL,
                                      editorial     VARCHAR(1000)
                                      );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(*args, **kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM PROBLEMS
                                    WHERE (""" + ' '.join([key + ' = ' + str(kwargs[key]) for key in kwargs]) + """);"""
            cursor.execute(statement)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return [Problems.object_converter(row) for row in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM PROBLEMS"""
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result

    @staticmethod
    def object_converter(values):
        problem = Problems('a', 'b')

        for ind, field in enumerate(Problems.fields):
            problem.__setattr__(field, values[ind])

        return problem
