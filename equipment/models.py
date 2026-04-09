from django.db import models
from stations.models import Station

# Create your models here.
class Lines(models.Model):
    name = models.CharField( max_length=128)
    nomenclature = models.CharField( max_length=128)
    voltage_level = models.CharField( max_length=50)
    station = models.ForeignKey(Station, on_delete=models.DO_NOTHING)
    line_type = models.CharField( max_length=50)
    approve_date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    check_14_days = models.BooleanField(default=True)
    created_at = models.DateTimeField( auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Equipment(models.Model):
    name = models.CharField( max_length=128)
    equipment_type = models.CharField(max_length=32, null=True)
    nomenclature = models.CharField( max_length=50)
    volttage_level = models.CharField( max_length=50)
    station = models.ForeignKey(Station, on_delete=models.DO_NOTHING)
    approve_date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    check_14_days = models.BooleanField(default=True)
    created_at = models.DateTimeField( auto_now_add=True)
    
    def __str__(self):
        return self.name