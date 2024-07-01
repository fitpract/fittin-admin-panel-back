from django.db import models

from catalog.models import Product


class Storage(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    location = models.CharField(max_length=255, blank=False)
    coordinates = models.CharField(max_length=100, default='')

    class Meta:
        db_table = 'storage'


class ProductStorage(models.Model):
    id = models.BigAutoField(primary_key=True)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    count_product = models.IntegerField('count_product', default=0)

    class Meta:
        db_table = 'product_storage'
        unique_together = ('storage', 'product')
