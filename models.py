from . import db

class Cart(db.Model):
    product = db.Column(db.String(100), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self, product, quantity):
        self.product=product
        self.quantity=quantity
