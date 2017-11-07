import psycopg2 as dbapi2
from flask import current_app

class Blog:

    def __init__(self,blog_id, user_id, blog_content,post_time, vote,hits):
        self.blog_id = blog_id
        self.user_id = user_id
        self.blog_content = blog_content
        self.post_time = post_time
        self.vote = vote
        self.hits= hits

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO BLOG (blog_id, user_id, blog_content , post_time,vote,hits) VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, [self.blog_id, self.user_id, self.blog_content, self.post_time, self.vote, self.hits])
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM BLOG WHERE blog_id=%s"""
            cursor.execute(query, [self.blog_id])
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE BLOG SET  (blog_id, user_id, blog_content , post_time) VALUES (%s, %s, %s, %s, %s)"""
            cursor.execute(query, [self.blog_id, self.user_id, self.blog_content, self.post_time,self.vote, self.hits])
            connection.commit()

    @staticmethod
    def get(blog_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM BLOG WHERE blog_id=%s"""
            cursor.execute(query, [blog_id])
            result = cursor.fetchall()
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM BLOG """
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result
