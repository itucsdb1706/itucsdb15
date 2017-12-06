import psycopg2 as dbapi2
from flask import current_app


class Clarification:
    fields = ['clarification_id', 'contest_id', 'user_id', 'clarification_content']

    def __init__(self, contest_id=None, user_id=None, clarification_content=None):
        self.clarification_id = None
        self.contest_id = contest_id
        self.user_id = user_id
        self.clarification_content = clarification_content

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO CLARIFICATION (contest_id, user_id, clarification_content) 
                                      VALUES (%s, %s, %s) 
                                      RETURNING clarification_id;"""
            cursor.execute(statement, (self.contest_id,
                                       self.user_id,
                                       self.clarification_content))
            self.clarification_id = cursor.fetchone()[0]
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
                                  SET contest_id = %s, user_id = %s, clarification_content = %s
                                  WHERE (clarification_id = %s);"""
            cursor.execute(statement, (self.contest_id,
                                       self.user_id,
                                       self.clarification_content,
                                       self.clarification_id))
            cursor.close()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS CLARIFICATION (
                                      clarification_id      SERIAL PRIMARY KEY NOT NULL,
                                      contest_id            INTEGER REFERENCES CONTEST(contest_id) ON DELETE CASCADE 
                                                            NOT NULL,
                                      user_id               INTEGER REFERENCES USERS(user_id) ON DELETE CASCADE 
                                                            NOT NULL,
                                      clarification_content VARCHAR(512)
                                      );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(*args, **kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM CLARIFICATION
                                  WHERE (""" + ' '.join([key + ' = ' + str(kwargs[key]) for key in kwargs]) + """);"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return [Clarification.object_converter(item) for item in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM CLARIFICATION;"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return result

    @staticmethod
    def object_converter(values):
        clarification = Clarification()

        for ind, field in enumerate(Clarification.fields):
            clarification.__setattr__(field, values[ind])

        return clarification
