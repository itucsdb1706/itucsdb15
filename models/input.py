import psycopg2 as dbapi2
from flask import current_app


class Input:

    def __init__(self, problemID, testcase, expected_output):
        self.problemID = problemID
        self.testcase = testcase
        self.expected_output = expected_output


    def save(self):
        pass

    def delete(self, inputID):
        pass


    def update(self, inputID):
        pass

    def get(self, inputID):
        pass


    def get_all(self):
        pass
