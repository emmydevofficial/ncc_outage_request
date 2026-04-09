from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Staff

class StaffAdmin(UserAdmin):
    model = Staff

    # Define the fields to display in the list view
    list_display = ("username", "staff_no", "phone_num", "is_admin", "is_station_supervisor", "is_reviewer", "is_approver", "is_operator")

    # Add filters to the right panel
    list_filter = ("is_admin", "is_station_supervisor", "is_reviewer", "is_approver", "is_operator", "station", "region")

    # Define fieldsets for the detailed user edit page
    fieldsets = (
        ("Login Details", {"fields": ("username", "password")}),
        ("Personal Information", {"fields": ("first_name", "last_name", "email", "phone_num", "staff_no")}),
        ("Work Details", {"fields": ("station", "region")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_admin", "is_station_supervisor", "is_reviewer", "is_approver", "is_operator")}),
        ("Group Permissions", {"fields": ("groups", "user_permissions")}),
    )

    # Define the fields for the user creation form
    add_fieldsets = (
        ("Login Details", {"fields": ("username", "password1", "password2")}),
        ("Personal Information", {"fields": ("first_name", "last_name", "email", "phone_num", "staff_no")}),
        ("Work Details", {"fields": ("station", "region")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_admin", "is_station_supervisor", "is_reviewer", "is_approver", "is_operator")}),
    )

    search_fields = ("username", "email", "staff_no", "phone_num")
    ordering = ("username",)

# Register the custom Staff model with the custom admin class
admin.site.register(Staff, StaffAdmin)
