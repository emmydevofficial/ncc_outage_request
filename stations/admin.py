from django.contrib import admin
from .models import Station

class StationAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'phone_num', 'region', 'acc')
  list_display_links = ('id', 'name')
  list_filter = ('region',)
  search_fields = ('name', 'region', 'phone_num')
  list_per_page = 25

# Register your models here.
admin.site.register(Station, StationAdmin)