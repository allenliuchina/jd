from django.db import models


# Create your models here.
class Cart(models.Model):
    user = models.OneToOneField('user.models.User', models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
