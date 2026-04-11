from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_stations, name="all_stations"),
    path('add_station', views.add_station, name="add_station"),
    path('add_station_post', views.add_station_post, name="add_station_post"),
    path('bulk_station_post', views.bulk_station_post, name="bulk_station_post"),
    path('<int:station_id>/edit', views.edit_station, name="edit_station"),
    path('<int:station_id>/edit_post', views.edit_station_post, name="edit_station_post"),
    path('<int:station_id>/delete', views.delete_station, name="delete_station"),
]