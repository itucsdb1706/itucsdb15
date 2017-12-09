import psycopg2 as dbapi2
from flask import current_app
from datetime import datetime


class Contest:
    fields = ['contest_id', 'contest_name', 'is_individual', 'start_time', 'end_time']

    def __init__(self, contest_name=None, is_individual=None, start_time=None, end_time=None):
        self.contest_id = None
        self.contest_name = contest_name
        self.is_individual = is_individual
        self.start_time = start_time
        self.end_time = end_time

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO CONTEST (contest_name, is_individual, start_time, end_time) 
                                  VALUES (%s, %s, %s, %s);"""
            cursor.execute(statement, (self.contest_name,
                                       self.is_individual,
                                       self.start_time,
                                       self.end_time))
            self.contest_id = cursor.fetchone()[0]
            cursor.close()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM CONTEST 
                                  WHERE (contest_id = %s);"""
            cursor.execute(statement, (self.contest_id,))
            cursor.close()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE CONTEST
                                  SET contest_name = %s, is_individual = %s, start_time = %s, end_time = %s
                                  WHERE (contest_id = %s);"""
            cursor.execute(statement, (self.contest_name,
                                       self.is_individual,
                                       self.start_time,
                                       self.end_time,
                                       self.contest_id))
            cursor.close()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS CONTEST (
                                  contest_id    SERIAL PRIMARY KEY NOT NULL,
                                  contest_name  VARCHAR(256) NOT NULL,
                                  is_individual BOOLEAN NOT NULL,
                                  start_time    TIMESTAMP NOT NULL,
                                  end_time      TIMESTAMP NOT NULL 
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM CONTEST WHERE ( {} );"""\
                .format(', '.join(Contest.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            print(statement)
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            cursor.close()
            return [Contest.object_converter(row) for row in result]

    @staticmethod
    def get_with_problems(**kwargs):

        from .problems import Problems

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {}, {} FROM CONTEST INNER JOIN PROBLEMS ON (CONTEST.contest_id = PROBLEMS.contest_id)
                            WHERE ( {} );""".format(', '.join(map(lambda x: 'CONTEST.' + x, Contest.fields)),
                                                    ', '.join(map(lambda x: 'PROBLEMS.' + x, Problems.fields)),
                                                    'AND '.join([key + ' = %s' for key in kwargs]))
            print(statement)
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            cursor.close()

        return_list = []

        for i in range(len(result)):
            print(result[i])
            if i == 0:
                contest = Contest.object_converter(result[i])
                contest.problems = []

            contest.problems.append(Problems.object_converter(result[i][len(Contest.fields):]))

            if i == len(result)-1 or result[i+1][0] != result[i][0]:
                return_list.append(contest)

        return return_list

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM CONTEST ORDER BY start_time DESC, end_time;"""\
                .format(', '.join(Contest.fields))
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return [Contest.object_converter(row) for row in result]

    @staticmethod
    def object_converter(values):
        contest = Contest()

        for ind, field in enumerate(Contest.fields):
            contest.__setattr__(field, values[ind])

        if contest.end_time < datetime.now():
            contest.status = 'finished'
        elif contest.start_time <= datetime.now() <= contest.end_time:
            contest.status = 'active'
        else:
            contest.status = 'upcoming'

        return contest
