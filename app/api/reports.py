from flask import request, redirect, url_for, Blueprint, g
from db_connection import mysql
import datetime
import dateutil.parser

reports = Blueprint("reports", __name__, url_prefix='/reports')

@reports.route('/byweek', methods=['GET'])
def report_by_week_of_month():
    try:
        cursor = mysql.get_db().cursor()
        (fromDate, toDate) = (request.args['fromDate'], request.args['toDate'])
        cursor.execute("""select * from receipt 
                            where purchaseDate >= '{}' and purchaseDate <= '{}' and user_id='{}'""".format(fromDate, toDate, g.user_id))
        res = cursor.fetchall()
        if res:
            result = [{"name" : "week"+str(i), "among":0 } for i in range(1,5)]
            for x in res:
                convert_2_date = dateutil.parser.parse(x[1]).strftime('%d')
                if int(convert_2_date) < 8:
                    result[0]['among'] += float(x[2])
                elif int(convert_2_date) < 15:
                    result[1]['among'] += float(x[2])
                elif int(convert_2_date) < 22:
                    result[2]['among'] += float(x[2])
                else:
                    result[3]['among'] += float(x[2])
                
            return {"message": "success", "result": result}
        return {"message": "success", "result": res}
    except Exception as e:
        print(e)

@reports.route('/bycategory', methods=['GET'])
def report_by_category():
    try:
        cursor = mysql.get_db().cursor()
        (fromDate, toDate) = (request.args['fromDate'], request.args['toDate'])

        cursor.execute("""  select category.name, sum(receipt.total)
                            from receipt, category 
                            where purchaseDate >= '{}' and purchaseDate <= '{}' and receipt.user_id='{}'
                            and receipt.category_id = category.id
                            group by category.name """.format(fromDate, toDate, g.user_id))
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
