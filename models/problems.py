import psycopg2 as dbapi2
from flask import current_app


class Problems:
    """ Blueprint of PROBLEMS table """

    # Column names of PROBLEM table
    fields = ['problem_id', 'problem_name', 'statement', 'contest_id', 'max_score']

    def __init__(self, problem_name, statement, contest_id=None, max_score=0, problem_id=None):
        self.problem_id = problem_id
        self.problem_name = problem_name
        self.statement = statement
        self.contest_id = contest_id
        self.max_score = max_score

    def save(self):
        """
        Saves problem into database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO PROBLEMS (problem_name, statement, contest_id, max_score)""" \
                    + """VALUES (%s, %s, %s, %s) RETURNING problem_id;"""
            cursor.execute(query, (self.problem_name, self.statement, self.contest_id, self.max_score))
            self.problem_id = cursor.fetchone()[0]
            connection.commit()

    def delete(self):
        """
        Deletes problem from database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM PROBLEMS WHERE problem_id = %s;"""
            cursor.execute(query, [self.problem_id])
            connection.commit()

    def update(self):
        """
        Updates problem in database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE PROBLEMS SET (problem_name = %s, statement = %s, contest_id = %s, 
                        max_score = %s) WHERE (problem_id=%s);"""
            cursor.execute(query, (self.problem_name, self.statement, self.contest_id, self.max_score, self.problem_id))
            connection.commit()

    def get_sample(self):
        """
        Fetches sample input of problem.
        :return: None
        """

        from .input import Input

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM INPUT WHERE (problem_id = %s) ORDER BY input_id LIMIT 1;"""\
                .format(', '.join(Input.fields))
            cursor.execute(statement, (self.problem_id,))
            result = cursor.fetchall()
            cursor.close()

        self.sample = Input.object_converter(result[0])

    def get_tags(self):
        """
        Fetches tags of problem.
        :return: None
        """
        from .problem_tag import ProblemTag
        self.tags = ProblemTag.get_tags_for_problem(self)

    def get_discussions(self):
        """
        Fetches discussions of problem.
        :return: None
        """
        from .discussion import Discussion
        from .users import Users
        self.discussions = Discussion.get(problem_id=self.problem_id)
        for discussion in self.discussions:
            discussion.user = Users.get(user_id=discussion.user_id)[0]

    @staticmethod
    def create():
        """
        Creates PROBLEMS table in database.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS PROBLEMS (
                                      problem_id    SERIAL PRIMARY KEY NOT NULL,
                                      problem_name  VARCHAR(140),
                                      statement     VARCHAR(1000),
                                      contest_id    INTEGER REFERENCES CONTEST(contest_id) ON DELETE CASCADE NOT NULL,
                                      max_score     INT NOT NULL,
                                      editorial     VARCHAR(1000)
                                      );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get_with_submissions(problem_id, user_id):
        """
        Gets a problem from databse with submissions of given user
        :param problem_id: PK of the problem (int)
        :param user_id: PK of the user (int)
        :return: Problems with submissions (list)
        """

        from .submissions import Submissions

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {}, {} FROM PROBLEMS 
                                          INNER JOIN SUBMISSIONS ON (PROBLEMS.problem_id = SUBMISSIONS.problem_id)
                                          WHERE ( PROBLEMS.problem_id = %s AND SUBMISSIONS.user_id = %s )
                                          ORDER BY SUBMISSIONS.send_time DESC;"""\
                .format(', '.join(map(lambda x: 'PROBLEMS.' + x, Problems.fields)),
                        ', '.join(map(lambda x: 'SUBMISSIONS.' + x, Submissions.fields)))
            print(statement)
            cursor.execute(statement, (problem_id, user_id))
            result = cursor.fetchall()
            cursor.close()

        return_list = []

        for i in range(len(result)):
            print(result[i])
            if i == 0:
                problem = Problems.object_converter(result[i])
                problem.submissions = []

            problem.submissions.append(Submissions.object_converter(result[i][len(Problems.fields):]))

            if i == len(result)-1 or result[i+1][0] != result[i][0]:
                return_list.append(problem)

        if not return_list:
            return_list = Problems.get(problem_id=problem_id)
            return_list[0].submissions = []

        return return_list

    @staticmethod
    def get(**kwargs):
        """
        Queries problems from database according to given arguments.
        :param kwargs: Arguments
        :return: Problem list (list)
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM PROBLEMS WHERE ( {} );"""\
                .format(', '.join(Problems.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            connection.commit()
            print('AAAAAAAAAAa->', [Problems.object_converter(row) for row in result])
            return [Problems.object_converter(row) for row in result]

    @staticmethod
    def get_all():
        """
        Fetches all problems from database.
        :return: Problem list (list)
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT {} FROM PROBLEMS;""".format(', '.join(Problems.fields))
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return [Problems.object_converter(row) for row in result]

    @staticmethod
    def object_converter(values):
        """
        Creates a Problems object with given arguments.
        :param values: Fetched colums from database.
        :return: Problem (object)
        """
        problem = Problems('a', 'b')

        for ind, field in enumerate(Problems.fields):
            problem.__setattr__(field, values[ind])

        return problem

    @staticmethod
    def drop():
        """
        Drops PROBLEM table.
        :return: None
        """
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE  IF EXISTS PROBLEMS CASCADE;"""
            cursor.execute(statement)
            cursor.close()