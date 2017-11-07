import psycopg2 as dbapi2
from flask import current_app


class Comment:

    def __init__(self, blog_id, user_id, comment_content, post_time, vote):
        self.blog_id = blog_id
        self.user_id = user_id
        self.comment_content = comment_content
        self.post_time = post_time
        self.vote = vote

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO COMMENT (blog_id, user_id, comment_content ,post_time, vote)"""\
                    """VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (self.comment_id, self.blog_id, self.user_id, self.comment_content,
                                   self.post_time, self.vote))
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM COMMENT WHERE blog_id=%s"""
            cursor.execute(query, (self.blog_id))
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE COMMENT SET (comment_id, blog_id, user_id, comment_content, post_time, vote)"""\
                    """WHERE blod_id=%s VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (self.blog_id, self.comment_id, self.blog_id, self.user_id, self.comment_content,
                                   self.post_time, self.vote))
            connection.commit()

    @staticmethod
    def get(blog_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM COMMENT WHERE blog_id=%s"""
            cursor.execute(query, (blog_id))
            result = cursor.fetchall()
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM COMMENT """
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result
