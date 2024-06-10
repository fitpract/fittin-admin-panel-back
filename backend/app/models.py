from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True, blank=False)
    name = models.CharField('name', max_length=40, blank=False)
    surname = models.CharField('name', max_length=120, blank=False)
    password = models.CharField('password', max_length=255)
    is_staff = models.BooleanField(default=False)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField('name', max_length=255, unique=True)
    parent = models.CharField('parent', max_length=255, default='')
    child = models.CharField('child', max_length=255, default='')

    class Meta:
        db_table = 'category'


class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField('name', max_length=255, blank=False)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.IntegerField('price', blank=False)
    count = models.IntegerField('count', default=0)
    rating = models.IntegerField('rating', default=5)

    class Meta:
        db_table = 'product'


class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=100, default='formed')
    price = models.IntegerField('total_price')

    class Meta:
        db_table = 'order'


class OrderedProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField('amount', default=1)
    price = models.IntegerField('ordered_product_price')

    class Meta:
        db_table = 'orderedProduct'


class Storage(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    location = models.CharField(max_length=100)

    class Meta:
        db_table = 'Storage'


class ProductStorage(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    storage_id = models.ForeignKey(Storage, on_delete=models.CASCADE)
    count = models.IntegerField('amount', default=1)

    class Meta:
        db_table = 'ProductStorage'


class Banner(models.Model):
    id = models.BigAutoField(primary_key=True)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/banner_images/% Y/% m/% d/')
    header = models.CharField(max_length=100)
    description = models.CharField(max_length=100)

    class Meta:
        db_table = 'Banner'

