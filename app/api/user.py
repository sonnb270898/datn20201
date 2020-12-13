from flask_login import UserMixin
from db_connection import mysql

class User(UserMixin):
    def __init__(self, id, email, name, displayName='', photoURL=''):
        self.id = id
        self.email = email
        self.name = name
        self.displayName = displayName
        self.photoURL = photoURL
        
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
    def create_user(id, email, name, displayName='', photoURL=''):
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute(
                "INSERT INTO user (id, email, displayName, name, photoURL) "
                "VALUES (%s, %s, %s, %s, %s)",
                (id, email, displayName, name, photoURL),
            )
            # mysql.get_db().commit()
        except Exception as e:
            print(e)

    @staticmethod
    def edit_usercreate_user(id, email, name, displayName='', photoURL=''):
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute(
                "update user (id, email, displayName, name, photoURL) "
                "set (%s, %s, %s, %s, %s)",
                (id, email, displayName, name, photoURL),
            )
            # mysql.get_db().commit()
        except Exception as e:
            print(e)        