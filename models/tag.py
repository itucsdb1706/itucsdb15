import psycopg2 as dbapi2
from flask import current_app


class Tag:
    fields = ['tag_id', 'tag_name']

    def __init__(self, tag_name=None, tag_id=None):
        self.tag_id = tag_id
        self.tag_name = tag_name

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO TAG (tag_name) 
                                  VALUES (%s) 
                                  RETURNING tag_id;"""
            cursor.execute(statement, (self.tag_name,))
            self.tag_id = cursor.fetchone()[0]
            cursor.close()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM TAG 
                                  WHERE (tag_id = %s);"""
            cursor.execute(statement, (self.tag_id,))
            cursor.close()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE TAG 
                                  SET tag_name = %s 
                                  WHERE (tag_id = %s);"""
            cursor.execute(statement, (self.tag_name, self.tag_id))
            cursor.close()
