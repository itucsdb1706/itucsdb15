import psycopg2 as dbapi2
from flask import current_app


class Message:
    fields = ['message_id', 'message_content', 'is_read', 'from_user_id', 'to_user_id', 'time_sent']

    def __init__(self, message_content=None, is_read=False, from_user_id=None, to_user_id=None, time_sent=None,
                 message_id=None):
        self.message_content = message_content
        self.is_read = is_read
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.time_sent = time_sent
        self.message_id = message_id

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """INSERT INTO MESSAGE (message_content, is_read, from_user_id, to_user_id, time_sent) 
                                  VALUES (%s, %s, %s, %s, %s) 
                                  RETURNING message_id;"""
            cursor.execute(statement, (self.message_content,
                                       self.is_read,
                                       self.from_user_id,
                                       self.to_user_id,
                                       self.time_sent))
            self.message_id = cursor.fetchone()[0]
            cursor.close()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM MESSAGE
                                  WHERE (message_id = %s);"""
            cursor.execute(statement, (self.message_id,))
            cursor.close()

    def update_read(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE MESSAGE
                                  SET is_read = TRUE 
                                  WHERE (message_id = %s);"""
            cursor.execute(statement, (self.message_id,))
            cursor.close()

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS MESSAGE (
                                  message_id      SERIAL PRIMARY KEY NOT NULL,
                                  message_content VARCHAR(4096) NOT NULL,
                                  is_read         BOOLEAN NOT NULL DEFAULT FALSE,
                                  from_user_id    INTEGER REFERENCES USERS(user_id) NOT NULL,
                                  to_user_id      INTEGER REFERENCES USERS(user_id) NOT NULL,
                                  time_sent       TIMESTAMP NOT NULL
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT * FROM MESSAGE WHERE ( {} );"""\
                .format(' AND '.join([key + ' = %s' for key in kwargs]))
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            results = cursor.fetchall()
            cursor.close()
            return [Message.object_converter(row) for row in results]

    @staticmethod
    def get_messages_for_user(user):
        from models.users import Users

        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} 
                                  FROM MESSAGE INNER JOIN USERS ON (MESSAGE.from_user_id = USERS.user_id)
                                  WHERE (to_user_id = %s)
                                  ORDER BY time_sent DESC;""".format(Users.fields[1] + ', ' + ', '.join(Message.fields))
            cursor.execute(statement, (user.user_id,))
            results = cursor.fetchall()
            cursor.close()
            return [(item[0], Message.object_converter(item[1:])) for item in results]

    @staticmethod
    def drop():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE IF EXISTS MESSAGE CASCADE;"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def object_converter(values):
        message = Message()

        for ind, field in enumerate(Message.fields):
            message.__setattr__(field, values[ind])

        return message
