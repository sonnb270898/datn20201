from flask_login import UserMixin
from db_connection import mysql

class User(UserMixin):
    def __init__(self, id, email, name, dateOfBirth='', address=''):
        self.id = id
        self.email = email
        self.name = name
        self.dateOfBirth = dateOfBirth
        self.address = address
        
    @staticmethod
    def get_user(id):
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute("select * from user where id='{}'".format(id))
            user = cursor.fetchone()
            if user:
                return User(id=user[0], email=user[1], name=user[2])
            return None
        except Exception as e:
            print(e)

    @staticmethod
    def create_user(id, email, name, dateOfBirth='', address=''):
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute(
                "INSERT INTO user (id, email, name, dateOfBirth, address) "
                "VALUES (%s, %s, %s, %s, %s)",
                (id, email, name),
            )
            # mysql.get_db().commit()
        except Exception as e:
            print(e)

    @staticmethod
    def edit_user(id, email, name, dateOfBirth='', address=''):
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute(
                "update user (id, email, name, dateOfBirth, address) "
                "set (%s, %s, %s, %s, %s)",
                (id, email, name, dateOfBirth, address),
            )
            # mysql.get_db().commit()
        except Exception as e:
            print(e)        