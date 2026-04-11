from django.urls import path
from . import views

urlpatterns = [
    path('equipments', views.all_equipments, name="all_equipments"),
    path('equipments/add_equipment', views.add_equipment, name="add_equipment"),
    path('equipments/add_equipment_post', views.add_equipment_post, name="add_equipment_post"),
    path('equipments/bulk_equipment_post', views.bulk_equipment_post, name="bulk_equipment_post"),
    path('equipments/<int:equipment_id>/edit', views.edit_equipment, name="edit_equipments"),
    path('equipments/<int:equipment_id>/edit_post', views.edit_equipment_post, name="edit_equipment_post"),
    path('equipments/update_equipment_schedule', views.update_equipment_schedule, name="update_equipment_schedule"),
    path('equipments/<int:equipment_id>/delete', views.delete_equipment, name="delete_equipment"),

    
    path('lines', views.all_lines, name="all_lines"),
    path('lines/add_line', views.add_line, name="add_line"),
    path('lines/add_line_post', views.add_line_post, name="add_line_post"),
    path('lines/<int:line_id>/edit', views.edit_line, name="edit_line"),
    path('lines/<int:line_id>/edit_post', views.edit_line_post, name="edit_line_post"),
    path('lines/<int:line_id>/delete', views.delete_line, name="delete_line"),

]