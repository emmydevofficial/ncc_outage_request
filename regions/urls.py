from django.urls import path
from . import views

urlpatterns = [
    path('regions', views.all_regions, name="all_regions"),
    path('regions/add_region', views.add_region, name="add_region"),
    path('regions/add_region_post', views.add_region_post, name="add_region_post"),
    path('regions/<int:region_id>/edit', views.edit_region, name="edit_region"),
    path('regions/<int:region_id>/edit_post', views.edit_region_post, name="edit_region_post"),
    path('regions/<int:region_id>/delete', views.delete_region, name="delete_region"),
    
    
    path('accs', views.all_accs, name="all_accs"),
    path('accs/add_acc', views.add_acc, name="add_acc"),
    path('accs/add_acc_post', views.add_acc_post, name="add_acc_post"),
    path('accs/<int:acc_id>/edit', views.edit_acc, name="edit_acc"),
    path('accs/<int:acc_id>/edit_post', views.edit_acc_post, name="edit_acc_post"),
    path('accs/<int:acc_id>/delete', views.delete_acc, name="delete_acc"),
    
    path('get_accs/', views.get_accs, name='get_accs'),
    path('get_stations/', views.get_stations, name='get_stations'),
    path('get_stations_by_region/', views.get_stations_by_region, name='get_stations_by_region'),
    
]