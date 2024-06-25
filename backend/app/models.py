from django.db import models

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True, blank=False)
    name = models.CharField('name', max_length=40, blank=False)
    surname = models.CharField('name', max_length=120, blank=True)
    password = models.CharField('password', max_length=255, blank=False)
    is_staff = models.BooleanField(default=False)

    code = models.CharField(default='')
    code_expiration_time = models.DateTimeField(null=True, blank=True)

    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'user'


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


class Storage(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=False)
    location = models.CharField(max_length=100)

    class Meta:
        db_table = 'storage'


class ProductStorage(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    count = models.IntegerField('amount', default=1)

    class Meta:
        db_table = 'productStorage'


class Banner(models.Model):
    id = models.BigAutoField(primary_key=True)
    header = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=100, default='')
    products = models.ManyToManyField(Product, related_name='banners', blank=True)
    image = models.ImageField(upload_to='banner_image/', default=None)

    class Meta:
        db_table = 'banner'
