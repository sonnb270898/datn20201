from .receipts import receipts
from .products import products
from run import app

app.register_blueprint(receipts)
app.register_blueprint(products)