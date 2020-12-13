from flask import Flask
import logging as logger
from app import app


if __name__ == '__main__':
    from api import *
    app.run(debug=True, ssl_context="adhoc")
