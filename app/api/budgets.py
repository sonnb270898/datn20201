from flask import request, redirect, url_for, Blueprint
from db_connection import mysql
import datetime

budgets = Blueprint("budgets", __name__, url_prefix='/budgets')
user_id = 1

@budgets.route('/', methods=['GET'])
def get_all_budgets():
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from budget where user_id='{}'".format(user_id))
        budgets_list = cursor.fetchall()
        if budgets_list:
            result = list(map(lambda x: {
                "id": x[0],
                "among": x[1],
                "fromDate": x[2],
                "toDate": x[3],
            },budgets_list))
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@budgets.route('/<id>', methods=['GET'])
def get_budget(id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from budget where id={}".format(id))
        budget = cursor.fetchone()
        if budget:
            fromDate, toDate = budget[2].strftime("%Y-%m-%d"), budget[3].strftime("%Y-%m-%d")
            cursor.execute("select * from receipt where user_id='{}' and date >= '{}' and date <= '{}'".format(user_id, fromDate, toDate))
            receipt = cursor.fetchall()
            if receipt:
                result = list(map(lambda x: {
                    "id": x[0],
                    "date": x[1].strftime("%d/%m/%Y"),
                    "total": x[2],
                    "merchant": x[3],
                    },receipt))
                return {"message":"successful", "result":result}, 200
            return {"message":"successful", "result":[]}, 200
        return {"message":"No budget found", "result":[]}, 200
    except Exception as e:
        print(e)

@budgets.route('/', methods=['POST'])
def create_budget():
    try:
        (among, fromDate, toDate) = (request.form['among'], request.form['fromDate'], request.form['toDate'])
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                budget (among, fromDate, toDate, user_id) \
                values (%s,%s,%s,%s)",
                (among, fromDate, toDate, user_id))
        mysql.get_db().commit()

        result = {
            "among": among,
            "fromDate": fromDate,
            "toDate": toDate,
        }
        return {"message":"successful", "result": result}, 200
    except Exception as e:
        print(e)    

@budgets.route('/<id>', methods=['PUT'])
def update_budget(id):
    try:
        (among, fromDate, toDate) = (request.form['among'], request.form['fromDate'], request.form['toDate'])
        cursor = mysql.get_db().cursor()
        cursor.execute("update budget \
                        set among=%s, fromDate=%s, toDate=%s \
                        where id=%s", (among, fromDate, toDate, id))
        mysql.get_db().commit()
        result = {
            "id": id,
            "among": among,
            "fromDate": fromDate,
            "toDate": toDate,
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@budgets.route('/<id>', methods=['DELETE'])
def delete_product(id):
    pass

