from django.contrib import admin
from .models import Equipment, Lines

class EquipmentAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'nomenclature', 'station', 'voltage_level')
  list_display_links = ('id', 'name')
  list_filter = ('voltage_level', "station")
  search_fields = ('name', 'station', 'phone_num')
  list_per_page = 25


class LineAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'nomenclature', 'station', 'voltage_level', "line_type")
  list_display_links = ('id', 'name')
  list_filter = ('voltage_level', "line_type", "station")
  search_fields = ('name', 'station', 'phone_num')
  list_per_page = 25
  
# Register your models here.
admin.site.register(Equipment, EquipmentAdmin)
admin.site.register(Lines)
