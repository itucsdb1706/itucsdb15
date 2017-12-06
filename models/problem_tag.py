import psycopg2 as dbapi2
from flask import current_app


class ProblemTag:

    @staticmethod
    def get_tags_for_problem(problem_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT (tag_name) FROM 
                                  PROBLEM NATURAL JOIN PROBLEM_TAG NATURAL JOIN TAG
                                  WHERE (problem_id = %s);"""
            cursor.execute(statement, (problem_id,))
            tags_as_tuples = cursor.fetchall()
            cursor.close()
            return [item[0] for item in tags_as_tuples]
