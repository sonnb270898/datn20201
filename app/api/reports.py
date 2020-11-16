from flask import request, redirect, url_for, Blueprint, g
from db_connection import mysql
import datetime

reports = Blueprint("reports", __name__, url_prefix='/reports')

now = datetime.datetime.now()
user = 1

@reports.route('/', methods=['GET'])
def report_by_week_of_month():
    try:
        cursor = mysql.get_db().cursor()
        current_month = now.strftime('%m')
        current_year = now.strftime('%Y')
        month = request.args.get('month',current_month)
        year = request.args.get('year',current_year)
        cursor.execute("select * from receipt where date >= '{}' and user_id='{}'".format('-'.join([year, month, '01']), g.user_id))
        res = cursor.fetchall()
        if res:
            result = [{"name" : "week"+str(i), "among":0 } for i in range(1,5)]
            for x in res:
                if int(x[1].strftime('%d')) < 8:
                    result[1]['among'] += float(x[2])
                elif int(x[1].strftime('%d')) < 15:
                    result[2]['among'] += float(x[2])
                elif int(x[1].strftime('%d')) < 22:
                    result[3]['among'] += float(x[2])
                else:
                    result[4]['among'] += float(x[2])
                
            return {"message": "success", "result": result}
        return {"message": "success", "result": res}
    except Exception as e:
        print(e)

@reports.route('/bycategory', methods=['GET'])
def report_by_category():
    try:
        cursor = mysql.get_db().cursor()
        current_month = now.strftime('%m')
        current_year = now.strftime('%Y')
        month = request.args.get('month',current_month)
        year = request.args.get('year',current_year)

        cursor.execute("""  select category, sum(price)
                            from receipt, product 
                            where date >= '{}' and user_id='{}'
                            and receipt.id = product.receipt_id
                            group by category """.format('-'.join([year, month, '01']), g.user_id))
        res = cursor.fetchall()
        if res:
            result = list(map(lambda x:{
                "category":x[0],
                "among":x[1]
            },res))
            return {"message": "success", "result": result}
        return {"message": "success", "result": res}
    except Exception as e:
        print(e)
