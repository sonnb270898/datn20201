from flask import request, redirect, url_for, Blueprint, g
from db_connection import mysql
import datetime
import os
import sys
from os.path import dirname, join
import cv2
import numpy as np
from flask_login import login_required

# try:
#     sys.path.append(join(dirname(dirname(dirname(__file__))),'src/'))
#     from src.handle_img import *
#     from src.parse_config import ConfigParser

# except ImportError as e:
#     print('xxxxxxxxxx',e)

receipts = Blueprint("receipts", __name__, url_prefix='/receipts')

@receipts.route('/', methods=['GET'])
def get_all_receipts():
    try:
        cursor = mysql.get_db().cursor()
        if len(request.args) == 0:
                cursor.execute("select * from receipt where user_id='{}'".format(g.user_id))
        else:
            date = [request.args.get('year','2020'), request.args.get('month','01'), request.args.get('day','01')]
            cursor.execute("select * from receipt where date >= '{}' and user_id='{}' ".format('-'.join(date), g.user_id))
        receipts_list = cursor.fetchall()
        if receipts_list:
            result = list(map(lambda x: {
                "id": x[0],
                "date": x[1].strftime("%d/%m/%Y"),
                "total": x[2],
                "merchant": x[3],
                "category": x[4],
            },receipts_list))
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@receipts.route('/<id>', methods=['GET'])
def get_receipt(id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from receipt where id='{}' and user_id='{}'".format(id, g.user_id))
        receipt = cursor.fetchone()
        if receipt:
            result = {
                "id": receipt[0],
                "date": receipt[1].strftime("%d/%m/%Y"),
                "total": receipt[2],
                "merchant": receipt[3],
                "category": receipt[4],
            }
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@receipts.route('/', methods=['POST'])
def create_receipt():
    (date, total, merchant, category) = (request.form['date'], request.form['total'], request.form['merchant'], request.form['category'])
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                receipt (date,total,merchant,category,user_id) \
                values (%s,%s,%s,%s,%s)",
                (date, total, merchant, category, g.user_id))
        mysql.get_db().commit()
        r_id = cursor.lastrowid
        result = {
            "id": r_id,
            "date": date,
            "total": total,
            "merchant": merchant,
            "category": category,
        }
        return {"message":"successful", "result": result}, 200
    except Exception as e:
        print(e)    

@receipts.route('/upload', methods=['POST'])
def create_receipt_from_img():
    try:
        file, category = request.files['image'], request.form.get('category', '')
        image = np.asarray(bytearray(file.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        res = extract_receipt(image)
        print(res)
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                receipt (date, total, merchant, category, user_id) \
                values (%s,%s,%s,%s,%s)",
                (res['date'], float(res['total']), 'merchant', category, g.user_id))
        #get receipt_id
        receipt_id = cursor.lastrowid
        for p in res['pp']:
            cursor.execute("insert into \
                product (name, price, receipt_id) \
                values (%s,%s,%s,%s)",
                (p[0], float(p[1]), receipt_id))

        mysql.get_db().commit()
        return {"message":"successful", "result": res}, 200
    except Exception as e:
        print(e)
    

@receipts.route('/<id>', methods=['PUT'])
def update_receipt(id):
    try:
        (date, total, merchant, category) = (request.form['date'], request.form['total'], request.form['merchant'], request.form['category'])
        cursor = mysql.get_db().cursor()
        cursor.execute("update receipt \
                        set date=%s,total=%s,merchant=%s,category=%s \
                        where id=%s", (date, total, merchant, category, id))
        mysql.get_db().commit()
        result = {
            "id": id,
            "date": date,
            "total": total,
            "merchant": merchant,
            "category": category
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@receipts.route('/<id>', methods=['DELETE'])
def delete_receipt(id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("""
            delete from product
            where receipt_id = '{}'
        """.format(id))

        cursor.execute("""
            delete from receipt
            where id = '{}'
        """.format(id))

        mysql.get_db().commit()
        return {"message":"successful"}, 200
    except Exception as e:
        print(e)

