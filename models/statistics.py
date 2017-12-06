import psycopg2 as dbapi2
from flask import current_app


class Statistics:
    fields = ['statistics_id', 'top_language', 'most_solved_prob', 'most_tried_prob', 'most_solved_tag',
              'most_tried_tag', 'top_coder', 'top_blog', 'top_comment']

    def __init__(self, top_language=None, most_solved_prob=None, most_tried_prob=None, most_solved_tag=None,
                 most_tried_tag=None, top_coder=None, top_blog=None, top_comment=None):
        self.statistics_id = None
        self.top_language = top_language
        self.most_solved_prob = most_solved_prob
        self.most_tried_prob = most_tried_prob
        self.most_solved_tag = most_solved_tag
        self.most_tried_tag = most_tried_tag
        self.top_coder = top_coder
        self.top_blog = top_blog
        self.top_comment = top_comment

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO STATISTICS 
                                      (top_language, most_solved_prob, most_tried_prob, most_solved_tag, most_tried_tag, 
                                      top_coder, top_blog, top_comment) 
                                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                      RETURNING statistics_id;"""
            cursor.execute(statement, (self.top_language,
                                       self.most_solved_prob,
                                       self.most_tried_prob,
                                       self.most_solved_tag,
                                       self.most_tried_tag,
                                       self.top_coder,
                                       self.top_blog,
                                       self.top_comment))
            self.statistics_id = cursor.fetchone()[0]
            cursor.close()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM STATISTICS 
                                      WHERE (statistics_id = %s);"""
            cursor.execute(statement, (self.statistics_id,))
            cursor.close()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE STATISTICS
                                  SET top_language = %s, most_solved_prob = %s, most_tried_prob = %s, 
                                      most_solved_tag = %s, most_tried_tag = %s, top_coder = %s, top_blog = %s, 
                                      top_comment = %s
                                  WHERE (statistics_id = %s);"""
            cursor.execute(statement, (self.top_language,
                                       self.most_solved_prob,
                                       self.most_tried_prob,
                                       self.most_solved_tag,
                                       self.most_tried_tag,
                                       self.top_coder,
                                       self.top_blog,
                                       self.top_comment,
                                       self.statistics_id))
            cursor.close()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS STATISTICS (
                                  statistics_id     SERIAL PRIMARY KEY NOT NULL,
                                  top_language      VARCHAR(32),
                                  most_solved_prob  VARCHAR(256),
                                  most_tried_prob   VARCHAR(256),
                                  most_solved_tag   VARCHAR(64),
                                  most_tried_tag    VARCHAR(64),
                                  top_coder         VARCHAR(256),
                                  top_blog          VARCHAR(256),
                                  top_comment       VARCHAR(1024)
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(*args, **kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM STATISTICS
                                  WHERE (""" + ' '.join([key + ' = ' + str(kwargs[key]) for key in kwargs]) + """);"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return [Statistics.object_converter(item) for item in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM STATISTICS;"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return result

    @staticmethod
    def object_converter(values):
        statistics = Statistics()

        for ind, field in enumerate(Statistics.fields):
            statistics.__setattr__(field, values[ind])

        return statistics
