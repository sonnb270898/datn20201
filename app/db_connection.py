from flaskext.mysql import MySQL
from run import app

mysql = MySQL()
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = "root"
app.config['MYSQL_DATABASE_PASSWORD'] = ""
app.config['MYSQL_DATABASE_DB'] = "personal_finance"
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)