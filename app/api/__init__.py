from .receipts import receipts
# from .products import products
from .budgets import budgets
from .reports import reports
from .categories import categories
from .login import login_route

from app import app
from flask_login import current_user, login_required
from flask import url_for, redirect, g

def check_islogin():
    if not current_user.is_authenticated:
        return {"message":"You are not login"}
    else: 
        g.user_id = current_user.get_id()


app.before_request_funcs = {
    "receipts": [check_islogin],
    # "products":[check_islogin],
    "budgets": [check_islogin],
    "reports": [check_islogin],
    "categories": [check_islogin]
}


app.register_blueprint(receipts)
# app.register_blueprint(products)
app.register_blueprint(budgets)
app.register_blueprint(reports)
app.register_blueprint(categories)
app.register_blueprint(login_route)