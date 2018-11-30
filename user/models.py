from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Address(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    receiver = models.CharField(max_length=20, null=True)
    addr = models.CharField(max_length=150, null=True)
    phone = models.CharField(max_length=11, null=True)
    zip_code = models.CharField(max_length=6, null=True)
    is_default = models.BooleanField(default=False)
