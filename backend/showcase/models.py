from django.db import models
from catalog.models import Product

class Banner(models.Model):
    id = models.BigAutoField(primary_key=True)
    header = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=100, default='')
    products = models.ManyToManyField(Product, related_name='banners', blank=True)
    image = models.ImageField(upload_to='banner_image/', default=None)

    class Meta:
        db_table = 'banner'