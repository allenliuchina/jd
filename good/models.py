from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class GoodType(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='image/category/', null=True)  # 只能是相对路径

    def __str__(self):
        return self.name

    # def top(self):
    #     return Good.objects.filter(type=self).order_by('-sales')[:4]
    #

class Good(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(GoodType, on_delete=models.CASCADE, related_name='good', null=True)
    image = models.ImageField(upload_to='image/',null=True)
    price = models.FloatField(null=True)
    desc = models.TextField(null=True)
    create_time = models.DateTimeField(auto_now_add=True, null=True)
    sales = models.IntegerField(null=True, default=0)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Promotion(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='image/promotion')
    good = models.ForeignKey(Good, models.CASCADE)

    def __str__(self):
        return self.name


class GoodComment(models.Model):
    comment = models.CharField(max_length=150)
    create_time = models.DateTimeField(auto_now_add=True)
    good = models.ForeignKey(Good, models.CASCADE)
    user = models.ForeignKey(User, models.CASCADE)

    def __str__(self):
        return self.user.username
