from flask import request, redirect, url_for, Blueprint
from db_connection import mysql
import datetime

receipts = Blueprint("receipts", __name__, url_prefix='/receipts')
user = 1


@receipts.route('/', methods=['GET'])
def get_all_receipts():
    try:
        cursor = mysql.get_db().cursor()
        if len(request.args) == 0:
                cursor.execute("select * from receipt")
        else:
            date = [request.args.get('year','2020'), request.args.get('month','01'), request.args.get('day','01')]
            cursor.execute("select * from receipt where date > '{}' and user_id='{}' ".format('-'.join(date), user))
        receipts_list = cursor.fetchall()
        if receipts_list:
            result = list(map(lambda x: {
                "id": x[0],
                "date": x[1].strftime("%d/%m/%Y"),
                "total": x[2],
                "merchant": x[3],
            },receipts_list))
            return {"message":"successful", "result":result}, 200
        return {"message":"successful", "result":[]}, 200
    except Exception as e:
        print(e)

@receipts.route('/<id>', methods=['GET'])
def get_receipt(id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from receipt where id='{}'".format(id))
        receipt = cursor.fetchone()
        result = {
            "id": receipt[0],
            "date": receipt[1].strftime("%d/%m/%Y"),
            "total": receipt[2],
            "merchant": receipt[3],
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@receipts.route('/', methods=['POST'])
def create_receipt():
    (date, total, merchant) = (request.form['date'], request.form['total'], request.form['merchant'])
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                receipt (date,total,merchant,user_id) \
                values (%s,%s,%s,%s)",
                (date, total, merchant, user))
        mysql.get_db().commit()
        result = {
            "date": date,
            "total": total,
            "merchant": merchant,
        }
        return {"message":"successful", "result": result}, 200
    except Exception as e:
        print(e)    

@receipts.route('/<id>', methods=['PUT'])
def update_receipt(id):
    try:
        (date, total, merchant) = (request.form['date'], request.form['total'], request.form['merchant'])
        cursor = mysql.get_db().cursor()
        cursor.execute("update receipt \
                        set date=%s,total=%s,merchant=%s \
                        where id=%s", (date, total, merchant, id))
        mysql.get_db().commit()
        result = {
            "id": id,
            "date": date,
            "total": total,
            "merchant": merchant,
        }
        return {"message":"successful", "result":result}, 200
    except Exception as e:
        print(e)

@receipts.route('/<id>', methods=['DELETE'])
def delete_receipt(id):
    pass

