import psycopg2 as dbapi2
from flask import current_app
from models.tag import Tag
from models.problems import Problems


class ProblemTag:
    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS PROBLEM_TAG (
                                  problem_id INTEGER REFERENCES PROBLEMS(problem_id) ON DELETE CASCADE NOT NULL,
                                  tag_id     INTEGER REFERENCES TAG(tag_id) ON DELETE CASCADE NOT NULL,
                                  PRIMARY KEY (problem_id, tag_id)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def save_tags_to_problem(problem, tags_list):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO PROBLEM_TAG (problem_id, tag_id) 
                                  VALUES (%s, %s);"""
            cursor.executemany(statement, [(problem.problem_id, tag.tag_id) for tag in tags_list])
            cursor.close()

    @staticmethod
    def delete_tags_from_problem(problem, tags_list):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM PROBLEM_TAG
                                  WHERE (problem_id = %s AND tag_id = %s);"""
            cursor.executemany(statement, [(problem.problem_id, tag.tag_id) for tag in tags_list])
            cursor.close()

    @staticmethod
    def get_tags_for_problem(problem):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} 
                                  FROM PROBLEMS NATURAL JOIN PROBLEM_TAG NATURAL JOIN TAG
                                  WHERE (problem_id = %s);""".format(', '.join(Tag.fields))
            cursor.execute(statement, (problem.problem_id,))
            tags_as_tuples = cursor.fetchall()
            cursor.close()
            return [Tag.object_converter(item) for item in tags_as_tuples]

    @staticmethod
    def get_problems_with_tag(tag):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {}
                                  FROM PROBLEMS NATURAL JOIN PROBLEM_TAG NATURAL JOIN TAG
                                  WHERE (tag_id = %s);""".format(', '.join(Problems.fields))
            cursor.execute(statement, (tag.tag_id,))
            problems_as_tuples = cursor.fetchall()
            cursor.close()
            return [Problems.object_converter(item) for item in problems_as_tuples]

    @staticmethod
    def drop():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE  IF EXISTS PROBLEM_TAG CASCADE;"""
            cursor.execute(statement)
            cursor.close()
