from flask import request, redirect, url_for, Blueprint, g
from db_connection import mysql

categories = Blueprint("categories", __name__, url_prefix='/categories')

@categories.route('/', methods=['GET'])
def get_all_categories():
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from category where user_id='{}'".format(g.user_id))
        categories_list = cursor.fetchall()
        if categories_list:
            result = list(map(lambda x: {
                "id": x[0],
                "name": x[1],
                "icon": x[2]
            },categories_list))
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@categories.route('/', methods=['POST'])
def create_category():
    try:
        name, icon = request.json['name'], request.json['icon']
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                category (name, icon, user_id) \
                values (%s,%s,%s)",
                (name, icon, g.user_id))
        mysql.get_db().commit()
        c_id = cursor.lastrowid
        result = {
            "id": c_id,
            "name": name,
            "icon": icon
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@categories.route('/<id>', methods=['PUT'])
def update_category(id):
    try:
        name, icon = request.json['name'], request.json['icon']
        cursor = mysql.get_db().cursor()
        cursor.execute("""  update category
                            set name='{}', icon='{}'
                            where id='{}'""".format(name, icon, id))
        mysql.get_db().commit()
        result = {
            "id": id,
            "name": name,
            "icon": icon
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@categories.route('/<id>', methods=['DELETE'])
def delete_category(id):
    try:
        print(id)
        cursor = mysql.get_db().cursor()
        cursor.execute("""  delete from category 
                            where id='{}'""".format(id))
        mysql.get_db().commit()
        return {"message":"successful"}, 200
    except Exception as e:
        print(e)
