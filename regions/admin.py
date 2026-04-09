from django.contrib import admin
from .models import Region, ACC

class RegionAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'address', 'rom_name', 'rom_phone', 'roc_name', "roc_phone")
  list_display_links = ('id', 'name')
  #list_filter = ('name',)
  list_editable = ('rom_name',)
  search_fields = ('name', 'address', 'rom_name', 'rom_phone', 'roc_name', "roc_phone")
  list_per_page = 25
  
class ACCAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'region', 'phone_num')
  list_display_links = ('id', 'name')
  list_filter = ('name',)
  search_fields = ('name', 'region', 'phone_num')
  list_per_page = 25

# Register your models here.
admin.site.register(Region, RegionAdmin)
admin.site.register(ACC, ACCAdmin)