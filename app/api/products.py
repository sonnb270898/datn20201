# from flask import request, redirect, url_for, Blueprint
# from db_connection import mysql
# import datetime

# products = Blueprint("products", __name__, url_prefix='/receipts/<receipt_id>/products')

# @products.route('/', methods=['GET'])
# def get_all_products(receipt_id):
#     try:
#         cursor = mysql.get_db().cursor()
#         cursor.execute("select * from product where receipt_id='{}'".format(receipt_id))
#         products_list = cursor.fetchall()
#         if products_list:
#             result = list(map(lambda x: {
#                 "id": x[0],
#                 "name": x[1],
#                 "price": x[2],
#             },products_list))
#             return {"message":"successful", "result":result}, 200
#         return {"message":"successful", "result":[]}, 200
#     except Exception as e:
#         print(e)

# @products.route('/<id>', methods=['GET'])
# def get_product(receipt_id, id):
#     try:
#         cursor = mysql.get_db().cursor()
#         cursor.execute("select * from product where id='{}' ".format(id))
#         product = cursor.fetchone()
#         result = {
#             "id": product[0],
#             "name": product[1],
#             "price": product[2],
#         }
#         return {"message":"successful", "result":result}, 200
#     except Exception as e:
#         print(e)

# @products.route('/', methods=['POST'])
# def create_product(receipt_id):
#     try:
#         (name, price) = (request.form['name'], request.form['price'])
#         cursor = mysql.get_db().cursor()
#         cursor.execute("insert into \
#                 product (name, price, receipt_id) \
#                 values (%s,%s,%s)",
#                 (name, price, receipt_id))
#         mysql.get_db().commit()
#         p_id = cursor.lastrowid
#         result = {
#             "id": p_id,
#             "name": name,
#             "price": price,
#         }
#         return {"message": "insert successful", "result":result}, 200
#     except Exception as e:
#         print(e)    

# @products.route('/<id>', methods=['PUT'])
# def update_product(receipt_id, id):
#     try:
#         (name, price) = (request.form['name'], request.form['price'])
#         cursor = mysql.get_db().cursor()
#         cursor.execute("update product \
#                         set name=%s, price=%s \
#                         where id=%s", (name, price, id))
#         mysql.get_db().commit()
#         result = {
#             "id": id,
#             "name": name,
#             "price": price,
#         }
#         return {"message":"successful", "result":result}, 200
#     except Exception as e:
#         print(e)

# @products.route('/<id>', methods=['DELETE'])
# def delete_product(receipt_id, id):
#     try:
#         cursor = mysql.get_db().cursor()
#         cursor.execute("""
#             delete from product
#             where id = '{}'
#         """.format(id))
#         mysql.get_db().commit()
#         return {"message":"successful"}, 200
#     except Exception as e:
#         print(e)

