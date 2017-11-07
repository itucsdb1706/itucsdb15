import psycopg2 as dbapi2
from flask import current_app

class Team:

    def __init__(self, team_id, team_name, team_rank , team_photo):
        self.team_id = team_id
        self.team_name = team_name
        self.team_rank = team_rank
        self.team_photo = team_photo

    def save(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """INSERT INTO TEAM (team_id, team_name, team_rank , team_photo) VALUES (%s, %s, %s, %s)"""
            cursor.execute(query, [self.team_id, self.team_name, self.team_rank, self.team_photo])
            connection.commit()

    def delete(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """DELETE FROM TEAM WHERE team_id=%s"""
            cursor.execute(query, [self.team_id])
            connection.commit()

    def update(self):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """UPDATE TEAM SET  (team_id, team_name, team_rank , team_photo) VALUES (%s, %s, %s)"""
            cursor.execute(query, [self.team_id, self.team_name, self.team_rank, self.team_photo])
            connection.commit()

    @staticmethod
    def get(team_id):
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM TEAM WHERE team_id=%s"""
            cursor.execute(query, [team_id])
            result = cursor.fetchall()
            connection.commit()
            return result

    @staticmethod
    def get_all():
        with dbapi2.connect(current_app.config['dsn']) as connection:
            cursor = connection.cursor()
            query = """SELECT * FROM TEAM """
            cursor.execute(query)
            result = cursor.fetchall()
            # TODO: None check
            connection.commit()
            return result
