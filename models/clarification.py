import psycopg2 as dbapi2
from flask import current_app

from models.contest import Contest


class Clarification:
    fields = ['clarification_id', 'contest_id', 'user_id', 'time_sent', 'clarification_content']

    def __init__(self, contest_id=None, user_id=None, time_sent=None, clarification_content=None,
                 clarification_id=None):
        self.contest_id = contest_id
        self.user_id = user_id
        self.time_sent = time_sent
        self.clarification_content = clarification_content
        self.clarification_id = clarification_id

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO CLARIFICATION (contest_id, user_id, time_sent,clarification_content) 
                                  VALUES (%s, %s, %s, %s) 
                                  RETURNING clarification_id;"""
            cursor.execute(statement, (self.contest_id,
                                       self.user_id,
                                       self.time_sent,
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

    def update_content(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE CLARIFICATION
                                  SET clarification_content = %s, time_sent = %s
                                  WHERE (clarification_id = %s);"""
            cursor.execute(statement, (self.clarification_content,
                                       self.time_sent,
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
                                  user_id               INTEGER REFERENCES USERS(user_id) ON DELETE CASCADE NOT NULL,
                                  time_sent             TIMESTAMP NOT NULL,
                                  clarification_content VARCHAR(2048) NOT NULL 
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            where_cond = ' AND '.join([key + ' = %s' for key in kwargs])
            statement = """SELECT * FROM CLARIFICATION WHERE (""" + where_cond + """);"""
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            cursor.close()
            return [Clarification.object_converter(item) for item in result]

    @staticmethod
    def get_clarifications_for_user(user):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} 
                                  FROM CLARIFICATION NATURAL JOIN CONTEST 
                                  WHERE (user_id = %s)
                                  ORDER BY time_sent DESC;""".format(Contest.fields[1] + ', '
                                                                     + ', '.join(Clarification.fields))
            cursor.execute(statement, (user.user_id,))
            result = cursor.fetchall()
            cursor.close()
            return [(item[0], Clarification.object_converter(item[1:])) for item in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM CLARIFICATION;"""
            cursor.execute(statement)
            result = cursor.fetchall()
            cursor.close()
            return [Clarification.object_converter(item) for item in result]

    @staticmethod
    def object_converter(values):
        clarification = Clarification()

        for ind, field in enumerate(Clarification.fields):
            clarification.__setattr__(field, values[ind])

        return clarification

    @staticmethod
    def drop():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE CLARIFICATION;"""
            cursor.execute(statement)
            cursor.close()
