from flask import request, redirect, url_for, Blueprint
from db_connection import mysql
import datetime

receipts = Blueprint("receipts", __name__, url_prefix='/receipts')

@receipts.route('/', methods=['GET'])
def get_all_receipts():
    if len(request.args) == 0:
        try:
            cursor = mysql.get_db().cursor()
            cursor.execute("select * from receipt")
            result = cursor.fetchall()
            res = list(map(lambda x: {
                "id": x[0],
                "date": x[1].strftime("%d/%m/%Y"),
                "total": x[2],
                "merchant": x[3],
            },result))
            return {"result":res}, 200
        except Exception as e:
            print(e)
    else:
        try:
            date = [request.args.get('year','2020'), request.args.get('month','01'), request.args.get('day','01')]
            print('select * from receipt where date > {}'.format('-'.join(date)))
            cursor = mysql.get_db().cursor()
            cursor.execute("select * from receipt where date > '{}'".format('-'.join(date)))
            result = cursor.fetchall()
            res = list(map(lambda x: {
                "id": x[0],
                "date": x[1].strftime("%d/%m/%Y"),
                "total": x[2],
                "merchant": x[3],
            },result))
            return {"result":res}, 200
        except Exception as e:
            print(e)

@receipts.route('/<id>', methods=['GET'])
def get_receipt(id):
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("select * from receipt where id='{}'".format(id))
        result = cursor.fetchone()
        result = {
            "id": result[0],
            "date": result[1].strftime("%d/%m/%Y"),
            "total": result[2],
            "merchant": result[3],
        }
        return {"result":result}, 200
    except Exception as e:
        print(e)

@receipts.route('/', methods=['POST'])
def create_receipt():
    user = 1
    try:
        cursor = mysql.get_db().cursor()
        cursor.execute("insert into \
                receipt (date,total,merchant,user_id) \
                values (%s,%s,%s,%s)",
                (request.form['date'],request.form['total'],request.form['merchant'],user))
        # mysql.get_db().commit()
        return {"message": "insert successful"}, 200
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

@receipts.route('/<id>', methods=['DELETE'])
def delete_receipt(id):
    pass

