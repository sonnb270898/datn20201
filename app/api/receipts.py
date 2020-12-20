from flask import request, redirect, url_for, Blueprint, g
from db_connection import mysql
import datetime
import os
import sys
from os.path import dirname, join
import cv2
import numpy as np
from flask_login import login_required
from werkzeug.utils import secure_filename
import uuid

import time 
UPLOAD_FOLDER = os.path.join(dirname(dirname(__file__)),'static')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
try:
    sys.path.append(join(dirname(dirname(dirname(__file__))),'src/'))
    from src.handle_img import *
    from src.parse_config import ConfigParser
except ImportError as e:
    print(e)

receipts = Blueprint("receipts", __name__, url_prefix='/receipts')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@receipts.route('/', methods=['GET'])
def get_all_receipts():
    try:
        cursor = mysql.get_db().cursor()

        fromDate, toDate = request.args.get("fromDate",""), request.args.get("toDate","")
        cursor.execute("""  select r.*, c.name 
                            from receipt r, category c
                            where r.user_id='{}' and r.category_id = c.id and
                            r.purchaseDate >= '{}' and r.purchaseDate <= '{}'
                            """.format(g.user_id, fromDate, toDate))
        receipts_list = cursor.fetchall()
        
        if receipts_list:
            result = list(map(lambda x: {
                "id": x[0],
                "purchaseDate": x[1],
                "total": x[2],
                "merchant": x[3],
                "url_image": x[4],
                "category": x[7],
                "user_id": g.user_id
            },receipts_list))
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@receipts.route('/<id>', methods=['GET'])
def get_receipt(id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("""  select r.*, c.name 
                            from receipt r, category c 
                            where r.id='{}' and r.category_id = c.id
                            and r.user_id='{}'""".format(id, g.user_id))
        receipt = cursor.fetchone()

        cursor.execute("""  select *
                            from product
                            where receipt_id={}""".format(id))
        
        products_in_receipt = cursor.fetchall()
        products = []
        if products_in_receipt:
            products = list(map(lambda x: {
                "id":x[0],
                "name":x[1],
                "price":x[2],
            },products_in_receipt))

        if receipt:
            result = {
                "id": receipt[0],
                "purchaseDate": receipt[1],
                "total": receipt[2],
                "merchant": receipt[3],
                "url_image": receipt[4],
                "category": receipt[7],
                "products": products,
                "user_id": g.user_id
                
            }
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":{}}, 200
    except Exception as e:
        print(e)

@receipts.route('/', methods=['POST'])
def create_receipt():
    try:
        (purchaseDate, total, merchant, category_id, url_image) = (request.json.get("purchaseDate",""), request.json.get("total",""),\
                                                                request.json.get("merchant",""), request.json.get("category_id",""), request.json.get("url_image",""))
        products = request.json["products"]
    
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                receipt (purchaseDate, total, merchant, url_image, category_id, user_id) \
                values (%s,%s,%s,%s,%s,%s)",
                (purchaseDate, total, merchant, url_image, category_id, g.user_id))
        mysql.get_db().commit()
        r_id = cursor.lastrowid
        
        products_query = ",".join(["('{}','{}','{}')".format(x["name"], x["price"], r_id) for x in products])
        cursor.execute("insert into \
                product (name, price, receipt_id) \
                values "+ products_query)
        mysql.get_db().commit()

        result = {
            "id": r_id,
            "purchaseDate": purchaseDate,
            "total": total,
            "merchant": merchant,
            "category_id": category_id,
            "url_image": url_image,
            "products": products,
            "user_id": g.user_id
        }
        return {"message":"successful", "result": result}, 200
    except Exception as e:
        print(e)    

@receipts.route('/upload', methods=['POST'])
def create_receipt_from_img():
    try:
        
        file = request.files['image']
        
        #conversion image
        image = np.fromstring(file.read(), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        
        #extract data
        res = extract_receipt(image)
        
        filename = str(uuid.uuid4()) + secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        url_image = "https://localhost:5000/static/" + filename

        # cursor = mysql.get_db().cursor()
        # cursor.execute("insert into \
        #         receipt (purchaseDate, total, merchant, url_image, category_id, user_id) \
        #         values (%s,%s,%s,%s,%s,%s)",
        #         (res['date'], float(res['total']), res['company'], url_image, category_id, g.user_id))
        # #get receipt_id
        # receipt_id = cursor.lastrowid
        
        # pp_value = ','.join(["('{}','{}','{}')".format(p[0], float(p[1]), receipt_id) for p in res['pp']])
        # cursor.execute("insert into \
        #     product (name, price, receipt_id) \
        #     values " + pp_value)

        # mysql.get_db().commit()
        res['url_image'] = url_image
        
        return {"message":"successful", "result": res}, 200
    except Exception as e:
        print(e)
    

@receipts.route('/<id>', methods=['PUT'])
def update_receipt(id):
    try:
        (purchaseDate, total, merchant, category_id, url_image) = (request.json.get("purchaseDate",""), request.json.get("total",""),\
                                                                request.json.get("merchant",""), request.json.get("category_id",""), request.json.get("url_image",""))
        products = request.json['products']
        cursor = mysql.get_db().cursor()

        cursor.execute("""
            delete from product
            where receipt_id = '{}'
        """.format(id))

        cursor.execute("update receipt \
                        set purchaseDate=%s, total=%s, merchant=%s, category_id=%s, url_image=%s \
                        where id=%s", (purchaseDate, total, merchant, category_id, url_image, id))
        
        products_query = ",".join(["('{}','{}','{}')".format(x["name"],x["price"],id) for x in products])
        cursor.execute("insert into \
                product (name, price, receipt_id) \
                values "+products_query)
        mysql.get_db().commit()

        result = {
            "id": id,
            "purchaseDate": purchaseDate,
            "total": total,
            "merchant": merchant,
            "category_id": category_id,
            "url_image": url_image,
            "products": products,
            "user_id": g.user_id
        }
        return {"message":"successful", "result": result}, 200
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

