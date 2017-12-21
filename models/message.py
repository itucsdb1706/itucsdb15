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
        """Saves this message object to the database, also assigns the id of the message in the database to the
            object"""
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
        """Deletes this message inside the database by using its id"""
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DELETE FROM MESSAGE
                                  WHERE (message_id = %s);"""
            cursor.execute(statement, (self.message_id,))
            cursor.close()

    def update_read(self):
        """Updates the read-state of this message in the database and the object to True"""
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """UPDATE MESSAGE
                                  SET is_read = TRUE 
                                  WHERE (message_id = %s);"""
            cursor.execute(statement, (self.message_id,))
            self.is_read = True
            cursor.close()

    @staticmethod
    def create():
        """Executes the create statement for the MESSAGE table in the database"""
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS MESSAGE (
                                  message_id      SERIAL PRIMARY KEY NOT NULL,
                                  message_content VARCHAR(4096) NOT NULL,
                                  is_read         BOOLEAN NOT NULL DEFAULT FALSE,
                                  from_user_id    INTEGER REFERENCES USERS(user_id) ON DELETE CASCADE NOT NULL,
                                  to_user_id      INTEGER REFERENCES USERS(user_id) ON DELETE CASCADE NOT NULL,
                                  time_sent       TIMESTAMP NOT NULL
                                  );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        """Generic get command with flexible arguments for message fetching from the database
            :returns list of fetched message objects"""
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
        """Fetches the messages sent to a certain user, given the user
            :returns list of tuples such that element [0] is a string containing the sender's username and element [1]
            is the message object sent by that user"""
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
        """Executes the drop statement to the MESSAGE table"""
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """DROP TABLE IF EXISTS MESSAGE CASCADE;"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def object_converter(values):
        """Generic message object conversion method for converting the tuples returned from select statements
            :returns message object that wraps the values in the tuple list"""
        message = Message()

        for ind, field in enumerate(Message.fields):
            message.__setattr__(field, values[ind])

        return message
