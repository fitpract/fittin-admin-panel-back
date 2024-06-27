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