from flask import Flask
import logging as logger

logger.basicConfig(level="DEBUG")

app = Flask(__name__)

if __name__ == '__main__':
    from api import *
    app.run(debug=True)
