from django.db import models

# Create your models here.
class Region(models.Model):
    name = models.CharField( max_length=50)
    address = models.TextField(max_length=1024)
    rom_name = models.CharField( max_length=128)
    rom_email = models.EmailField( max_length=254)
    rom_phone = models.CharField(max_length=20)
    roc_name = models.CharField( max_length=128)
    roc_email = models.EmailField( max_length=254)
    roc_phone = models.CharField(max_length=20)
    short_code = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    

class ACC(models.Model):
    name = models.CharField( max_length=128)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING)
    email = models.EmailField( max_length=254)
    location = models.CharField( max_length=50)
    state = models.CharField( max_length=50)
    phone_num = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    