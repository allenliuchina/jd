from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
