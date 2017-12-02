import psycopg2 as dbapi2
from flask import current_app


class Clarification:
    def __init__(self, clarification_id, contest_id, user_id, clarification_content):
        self.clarification_id = clarification_id
        self.contest_id = contest_id
        self.user_id = user_id
        self.clarification_content = clarification_content

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO CLARIFICATION (clarification_id ,contest_id, user_id, clarification_content) 
                                      VALUES (%s ,%s, %s, %s);"""
            cursor.execute(statement, (self.clarification_id,
                                       self.contest_id,
                                       self.user_id,
                                       self.clarification_content))
            cursor.close()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM CLARIFICATION 
                                      WHERE (clarification_id = %s);"""
            cursor.execute(statement, (self.clarification_id,))
            cursor.close()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE CLARIFICATION
                                  SET (contest_id = %s, user_id = %s, clarification_content = %s)
                                  WHERE (clarification_id = %s);"""
            cursor.execute(statement, (self.contest_id,
                                       self.user_id,
                                       self.clarification_content,
                                       self.clarification_id))
            cursor.close()

    @staticmethod
    def get(clarification_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM CLARIFICATION
                                  WHERE (clarification_id = %s);"""
            cursor.execute(statement, (clarification_id,))
            result = cursor.fetchone()
            cursor.close()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM CLARIFICATION;"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return result
