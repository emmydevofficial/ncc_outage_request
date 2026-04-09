from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from stations.models import Station
from regions.models import Region

class Staff(AbstractUser):
    staff_no = models.CharField(max_length=50)
    station = models.ForeignKey(Station, on_delete=models.DO_NOTHING, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.DO_NOTHING, blank=True, null=True)
    phone_num = models.CharField(max_length=20)
    is_station_supervisor = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_reviewer = models.BooleanField(default=False)
    is_approver = models.BooleanField(default=False)
    is_operator = models.BooleanField(default=False)

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(Group, related_name="staff_users", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="staff_user_permissions", blank=True)
    
    def __str__(self):
        return self.first_name
    