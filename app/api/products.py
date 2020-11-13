from flask import request, redirect, url_for, Blueprint
from db_connection import mysql
import datetime

products = Blueprint("products", __name__, url_prefix='/receipts/<receipt_id>/products')

@products.route('/', methods=['GET'])
def get_all_products(receipt_id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from product where receipt_id='{}'".format(receipt_id))
        result = cursor.fetchall()
        res = list(map(lambda x: {
            "id": x[0],
            "name": x[1],
            "price": x[2],
            "category": x[3],
        },result))
        return {"result":res}, 200
    except Exception as e:
        print(e)

@products.route('/<id>', methods=['GET'])
def get_product(receipt_id, id):
    print(id)
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from product where id='{}' ".format(id))
        result = cursor.fetchone()
        result = {
            "id": result[0],
            "name": result[1],
            "price": result[2],
            "category": result[3],
        }
        return {"result":result}, 200
    except Exception as e:
        print(e)

@products.route('/', methods=['POST'])
def create_product(receipt_id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                product (name, price, category, receipt_id) \
                values (%s,%s,%s,%s)",
                (request.form['name'],request.form['price'],request.form['category'], receipt_id))
        # mysql.get_db().commit()
        return {"message": "insert successful"}, 200
    except Exception as e:
        print(e)    

@products.route('/<id>', methods=['PUT'])
def update_product(receipt_id, id):

    (name, price, category) = (request.form['date'], request.form['total'], request.form['merchant'])
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("update product \
                        set name=%s, price=%s, category=%s \
                        where id=%s", (name, price, category, id))
        # mysql.get_db().commit()
        result = {
            "id": id,
            "date": date,
            "total": total,
            "merchant": merchant,
        }
        return {"result":result}, 200
    except Exception as e:
        print(e)

@products.route('/<id>', methods=['DELETE'])
def delete_product(receipt_id, id):
    pass

