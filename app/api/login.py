import os
import json
import requests
from db_connection import mysql
from .user import User
from run import app
from flask import request, url_for, redirect, Blueprint
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
# from oauthlib.oauth2 import WebApplicationClient


login_route = Blueprint("login", __name__)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
login_manager = LoginManager()
login_manager.init_app(app)

# client = WebApplicationClient(os.environ.get("GOOGLE_CLIENT_ID"))

# def get_google_provider_cfg():
#     return requests.get(os.environ.get("GOOGLE_DISCOVERY_URL")).json()

@login_manager.user_loader
def load_user(email):
    return User.get_user(email)

# @login_route.route("/login")
# def login():
#     google_provider_cfg = get_google_provider_cfg()
#     authorization_endpoint = google_provider_cfg["authorization_endpoint"]
#     request_uri = client.prepare_request_uri(
#         authorization_endpoint,
#         redirect_uri= request.base_url + "/callback",
#         scope=["openid", "email", "profile"],
#     )
#     print(request_uri)
#     return redirect(request_uri)

# @login_route.route("/login/callback")
# def callback():
#     code = request.args.get("code")
#     google_provider_cfg = get_google_provider_cfg()
#     token_endpoint = google_provider_cfg["token_endpoint"]
#     token_url, headers, body = client.prepare_token_request(token_endpoint,
#                                                             authorization_response=request.url,
#                                                             redirect_url=request.base_url,
#                                                             code=code
#                                                             )
#     token_response = requests.post( token_url,
#                                     headers=headers,
#                                     data=body,
#                                     auth=(os.environ.get("GOOGLE_CLIENT_ID"), os.environ.get("GOOGLE_CLIENT_SECRET")),
#                                     )
#     client.parse_request_body_response(json.dumps(token_response.json()))
#     userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
#     uri, headers, body = client.add_token(userinfo_endpoint)
#     userinfo_response = requests.get(uri, headers=headers, data=body)

#     if userinfo_response.json().get("email_verified"):
#         uid = userinfo_response.json()["sub"]
#         email = userinfo_response.json()["email"]
#         name = userinfo_response.json()["name"]

#     else:
#         return "User email not available or not verified by Google.", 400

#     user = User(id=uid, name=name, email=email)

#     if not User.get_user(uid):
#         User.create_user(uid, email, name)
#     login_user(user, remember=True)
#     return redirect(url_for('budgets.get_all_budgets'))

@login_route.route("/logout", methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@login_route.route("/login/user", methods=['GET'])
def check_user_login():
    uid = request.json["uid"]
    email = request.json["email"]
    name = request.json["name"]
    user = User(id=uid, name=name, email=email)

    if not User.get_user(uid):
        User.create_user(uid, email, name)
    login_user(user, remember=True)
    return redirect(url_for('receipt.get_all_receipts'))