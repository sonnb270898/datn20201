from flask import request, redirect, url_for, Blueprint
from db_connection import mysql
import datetime

products = Blueprint("products", __name__, url_prefix='/receipts/<receipt_id>/products')

@products.route('/', methods=['GET'])
def get_all_products(receipt_id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from product where receipt_id='{}'".format(receipt_id))
        products_list = cursor.fetchall()
        if products_list:
            result = list(map(lambda x: {
                "id": x[0],
                "name": x[1],
                "price": x[2],
                "category": x[3],
            },products_list))
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@products.route('/<id>', methods=['GET'])
def get_product(receipt_id, id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from product where id='{}' ".format(id))
        product = cursor.fetchone()
        result = {
            "id": product[0],
            "name": product[1],
            "price": product[2],
            "category": product[3],
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@products.route('/', methods=['POST'])
def create_product(receipt_id):
    try:
        (name, price, category) = (request.form['name'], request.form['price'], request.form['category'])
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                product (name, price, category, receipt_id) \
                values (%s,%s,%s,%s)",
                (name, price, category, receipt_id))
        mysql.get_db().commit()
        result = {
            "name": name,
            "price": price,
            "category": category,
        }
        return {"message": "insert successful", "result":result}, 200
    except Exception as e:
        print(e)    

@products.route('/<id>', methods=['PUT'])
def update_product(receipt_id, id):
    try:
        (name, price, category) = (request.form['name'], request.form['price'], request.form['category'])
        cursor = mysql.get_db().cursor()
        cursor.execute("update product \
                        set name=%s, price=%s, category=%s \
                        where id=%s", (name, price, category, id))
        mysql.get_db().commit()
        result = {
            "id": id,
            "name": name,
            "price": price,
            "category": category,
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@products.route('/<id>', methods=['DELETE'])
def delete_product(receipt_id, id):
    pass

