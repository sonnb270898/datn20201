from flask import request, redirect, url_for, Blueprint, g
from db_connection import mysql
import datetime

budgets = Blueprint("budgets", __name__, url_prefix='/budgets')

def get_product_in_receipt(receipt_id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("""  select * from product 
                            where receipt_id='{}'""".format(receipt_id))

        products = cursor.fetchall()
        if products:
            result = list(map(lambda x: {
                "id": x[0],
                "name": x[1],
                "price": x[2],
            },products))
            return result
        return []
    except Exception as e:
        print(e)

def get_receipt_in_budget(budget):
    try:
        cursor = mysql.get_db().cursor()
        among, fromDate, toDate, category_id, category = budget[1] ,budget[2], budget[3], budget[4], budget[5]
        cursor.execute("""  select r.*, c.name from receipt r, category c
                            where r.user_id='{}' and r.category_id=c.id and r.category_id={}
                            and purchaseDate >= '{}' and purchaseDate <= '{}'""".format(g.user_id, category_id, fromDate, toDate))

        receipt_list = cursor.fetchall()
        if receipt_list:
            result = list(map(lambda x: {
                "id": x[0],
                "purchaseDate": x[1],
                "total": x[2],
                "merchant": x[3],
                "url_image": x[4],
                "category": x[7],
                "products": get_product_in_receipt(x[0]),
                "user_id": g.user_id
            },receipt_list))
            return result
        return []
    except Exception as e:
        print(e)

@budgets.route('/', methods=['GET'])
def get_all_budgets():
    try:
        fromDate, toDate = request.args.get('fromDate',""), request.args.get('toDate',"")

        cursor = mysql.get_db().cursor()
        cursor.execute("""  select b.*, c.name from budget b, category c
                            where user_id='{}' and b.category_id = c.id and
                            b.fromDate >= '{}' and b.toDate <= '{}'""".format(g.user_id, fromDate, toDate))

        budgets_list = cursor.fetchall()
        if budgets_list:
            result = list(map(lambda x: {
                "id": x[0],
                "among": x[1],
                "fromDate": x[2],
                "toDate": x[3],
                "category": x[5],
                "receipts": get_receipt_in_budget(x)
            },budgets_list))
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@budgets.route('/', methods=['POST'])
def create_budget():
    try:
        (among, fromDate, toDate, category_id) = ( request.json.get('among',""), request.json.get('fromDate',""),\
                                                    request.json.get('toDate',""), request.json.get('category_id',""))
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                budget (among, fromDate, toDate, category_id) \
                values (%s,%s,%s,%s)",
                (among, fromDate, toDate, category_id))
        mysql.get_db().commit()
        b_id = cursor.lastrowid
        result = {
            "id": b_id,
            "among": among,
            "fromDate": fromDate,
            "toDate": toDate,
            "category_id":category_id
        }
        return {"message":"successful", "result": result}, 200
    except Exception as e:
        print(e)    

@budgets.route('/<id>', methods=['PUT'])
def update_budget(id):
    try:
        (among, fromDate, toDate, category_id) = ( request.json.get('among',""), request.json.get('fromDate',""),\
                                                    request.json.get('toDate',""), request.json.get('category_id',""))
        cursor = mysql.get_db().cursor()
        cursor.execute("update budget \
                        set among=%s, fromDate=%s, toDate=%s, category_id=%s \
                        where id=%s", (among, fromDate, toDate, category_id, id))
        mysql.get_db().commit()
        result = {
            "id": id,
            "among": among,
            "fromDate": fromDate,
            "toDate": toDate,
            "category_id":category_id
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@budgets.route('/<id>', methods=['DELETE'])
def delete_budget(id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute(""" 
            delete from budget
            where id = '{}'
        """.format(id))

        mysql.get_db().commit()
        return {"message":"successful"}, 200
    except Exception as e:
        print(e)

