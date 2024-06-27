from django.db import models
from user.models import User
from catalog.models import Product

class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='formed')
    price = models.IntegerField('total_price')

    class Meta:
        db_table = 'order'


class OrderedProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    price = models.IntegerField('ordered_product_price')

    class Meta:
        db_table = 'orderedProduct'