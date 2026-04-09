from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name="dashboard"),
    path('export_csv', views.export_requests_csv, name="export_requests_csv"),
]