import psycopg2 as dbapi2
from flask import current_app


class Statistics:
    def __init__(self, statistics_id, top_language, most_solved_prob, most_tried_prob, most_solved_tag, most_tried_tag,
                 top_coder, top_blog, top_comment):
        self.statistics_id = statistics_id
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
                                      (statistics_id, top_language, most_solved_prob, most_tried_prob, most_solved_tag, 
                                      most_tried_tag, top_coder, top_blog, top_comment) 
                                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(statement, (self.statistics_id,
                                       self.top_language,
                                       self.most_solved_prob,
                                       self.most_tried_prob,
                                       self.most_solved_tag,
                                       self.most_tried_tag,
                                       self.top_coder,
                                       self.top_blog,
                                       self.top_comment))
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
                                  SET (top_language = %s, most_solved_prob = %s, most_tried_prob = %s, 
                                      most_solved_tag = %s, most_tried_tag = %s, top_coder = %s, top_blog = %s, 
                                      top_comment = %s)
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
    def get(statistics_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM STATISTICS
                                  WHERE (statistics_id = %s);"""
            cursor.execute(statement, (statistics_id,))
            result = cursor.fetchone()
            cursor.close()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM STATISTICS;"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return result
