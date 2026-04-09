from django.contrib import admin
from .models import Request

class RequestAdmin(admin.ModelAdmin):
    # Define the fields to display in the list view
    list_display = ("id", "user", "station", "outage_type", "equipment", "line", "work_description", "is_reviewed", "seen_by_approval")
    list_display_links = ('id', 'work_description')
    list_filter = ('outage_type', "is_reviewed", "seen_by_approval")
    search_fields = ('user__username', 'station__name', 'equipment__name', 'work_description')
    list_per_page = 25

# Register your models here.
admin.site.register(Request, RequestAdmin)