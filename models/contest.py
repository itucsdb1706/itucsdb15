import psycopg2 as dbapi2
from flask import current_app
from datetime import datetime


class Contest:
    fields = ['contest_id', 'contest_name', 'is_individual', 'start_time', 'end_time']

    def __init__(self, contest_name=None, is_individual=True, start_time=None, end_time=None):
        self.contest_id = None
        self.contest_name = contest_name
        self.is_individual = is_individual
        self.start_time = start_time
        self.end_time = end_time

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO CONTEST (contest_name, is_individual, start_time, end_time) 
                                  VALUES (%s, %s, %s, %s) RETURNING contest_id;"""
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

    def get_problems(self):
        from .problems import Problems
        self.problems = Problems.get(contest_id=self.contest_id)

    def get_users(self):

        from .users import Users

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM CONTEST 
                                      INNER JOIN CONTEST_USERS ON (CONTEST.contest_id = CONTEST_USERS.contest_id)
                                      INNER JOIN USERS ON (CONTEST_USERS.user_id = USERS.user_id)
                                      WHERE (CONTEST.contest_id = %s);"""\
                .format(', '.join(map(lambda x: 'USERS.'+x, Users.fields)))
            cursor.execute(statement, (self.contest_id,))
            result = cursor.fetchall()
            cursor.close()

        self.users = [Users.object_converter(row) for row in result]

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS CONTEST (
                                  contest_id    SERIAL PRIMARY KEY NOT NULL,
                                  contest_name  VARCHAR(256) UNIQUE NOT NULL,
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
    def get_with_leaderboard(contest_name):

        from .problems import Problems
        from .submissions import Submissions
        from .users import Users

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()

            statement = """SELECT {}, {}, {}, MAX(SUBMISSIONS.score) FROM CONTEST 
        INNER JOIN CONTEST_USERS ON (CONTEST.contest_id = CONTEST_USERS.contest_id)
        INNER JOIN USERS ON (CONTEST_USERS.user_id = USERS.user_id)
        INNER JOIN PROBLEMS ON (CONTEST.contest_id = PROBLEMS.contest_id)
        INNER JOIN SUBMISSIONS ON (USERS.user_id = SUBMISSIONS.user_id AND SUBMISSIONS.problem_id = PROBLEMS.problem_id) 
        WHERE ( CONTEST.contest_name = %s )
        GROUP BY (CONTEST.contest_id, USERS.user_id, PROBLEMS.problem_id)
        ORDER BY MAX(SUBMISSIONS.score) DESC;"""\
                .format(', '.join(map(lambda x: 'CONTEST.'+x, Contest.fields)),
                        ', '.join(map(lambda x: 'USERS.'+x, Users.fields)),
                        ', '.join(map(lambda x: 'PROBLEMS.'+x, Problems.fields)),)
            print(statement)
            cursor.execute(statement, (contest_name,))
            result = cursor.fetchall()
            print(result)
            cursor.close()

        u_id = len(Contest.fields)
        p_id = len(Contest.fields)+len(Users.fields)

        if not result:
            return_dict = {'contest': Contest.get(contest_name=contest_name)[0], 'users': {}}
        else:
            return_dict = {'contest': Contest.object_converter(result[0]), 'users': {}}

        for i in range(len(result)):
            print(result[i])

            user = Users.object_converter(result[i][u_id:])
            problem = Problems.object_converter(result[i][p_id:])
            problem.score = result[i][-1]
            problem.is_complete = (problem.score == problem.max_score)

            if user.user_id not in return_dict['users']:
                user.problems = [problem]
                return_dict['users'][user.user_id] = user
            else:
                return_dict['users'][user.user_id].problems.append(problem)

        return return_dict

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

    @staticmethod
    def drop():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE  IF EXISTS CONTEST CASCADE;"""
            cursor.execute(statement)
            cursor.close()
