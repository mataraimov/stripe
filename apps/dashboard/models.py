from django.db import models


class Order(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False,default='order')
    price = models.IntegerField(default=0, null=False, blank=False)