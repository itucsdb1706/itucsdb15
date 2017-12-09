import psycopg2 as dbapi2
from flask import current_app


class Team:
    fields = ['team_id', 'team_name', 'team_rank', 'team_photo']

    def __init__(self, team_name, team_rank=0, team_photo=None):
        self.team_name = team_name
        self.team_rank = team_rank
        self.team_photo = team_photo

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO TEAM (team_name, team_rank , team_photo)
                        VALUES (%s, %s, %s, %s) RETURNING team_id;"""
            cursor.execute(query, (self.team_name, self.team_rank, self.team_photo))
            self.team_id = cursor.fetchone()[0]
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM TEAM WHERE team_id=%s"""
            cursor.execute(query, (self.team_id,))
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE TEAM SET team_name = %s, team_rank = %s , team_photo = %s) WHERE team_id = %s;"""
            cursor.execute(query, (self.team_name, self.team_rank, self.team_photo, self.team_id))
            connection.commit()

    def get_users(self):
        from .users import Users
        self.users = Users.get(team_id=self.team_id)
        return self.users

    @staticmethod
    def create():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """CREATE TABLE IF NOT EXISTS TEAM (
                                      team_id     SERIAL PRIMARY KEY NOT NULL,
                                      team_name   VARCHAR(128),
                                      team_rank   INT NOT NULL,
                                      team_photo  VARCHAR(4096)
                                      );"""
            cursor.execute(statement)
            cursor.close()

    @staticmethod
    def get(**kwargs):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            statement = """SELECT {} FROM TEAM WHERE ( {} );"""\
                .format(', '.join(Team.fields), 'AND '.join([key + ' = %s' for key in kwargs]))
            print(statement)
            cursor.execute(statement, tuple(str(kwargs[key]) for key in kwargs))
            result = cursor.fetchall()
            cursor.close()
            return [Team.object_converter(row) for row in result]

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT {} FROM TEAM;""".format(', '.join(Team.fields))
            cursor.execute(query)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result

    @staticmethod
    def object_converter():

        team = Team('a')

        for ind, field in enumerate(Team.fields):
            team.__setattr__(field, values[ind])

        return team
