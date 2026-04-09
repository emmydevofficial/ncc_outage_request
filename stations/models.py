from django.db import models
from regions.models import Region, ACC

# Create your models here.

class Station(models.Model):
    name = models.CharField( max_length=250)
    voltage_level = models.CharField( max_length=50)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING)
    acc = models.ForeignKey(ACC, on_delete=models.DO_NOTHING)
    location = models.CharField( max_length=50)
    state = models.CharField( max_length=50)
    phone_num = models.CharField(max_length=20)
    email = models.EmailField( max_length=254)
    
    def __str__(self):
        return self.name