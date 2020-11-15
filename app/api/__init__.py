from .receipts import receipts
from .products import products
from .budgets import budgets
from .reports import reports
from .login import login_route

from run import app

app.register_blueprint(receipts)
app.register_blueprint(products)
app.register_blueprint(budgets)
app.register_blueprint(reports)
app.register_blueprint(login_route)