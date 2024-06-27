from django.db import models


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField('name', max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    sorder_order = models.IntegerField('sorder_order', default=1)
    image = models.ImageField(upload_to='category_image/', blank=True)

    class Meta:
        db_table = 'category'


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField('name', max_length=255, blank=False, unique=True)
    brand = models.CharField('brand', max_length=255, blank=False,default='')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField('price', default=1)
    description = models.CharField('description', default='')
    count = models.IntegerField('count', default=0)
    rating = models.FloatField('rating', default=5)
    sorder_order = models.IntegerField('sorder_order', default=1)
    image = models.ImageField(upload_to='product_image/', blank=True)

    class Meta:
        db_table = 'product'