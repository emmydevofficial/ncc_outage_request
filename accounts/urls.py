from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_users, name="all_users"),
    path('add_user', views.add_user, name="add_user"),
    path("add_user_post", views.add_user_post, name="add_user_post"),
    path('<int:user_id>/edit', views.edit_user, name="edit_user"),
    path('<int:user_id>/edit_post', views.edit_user_post, name="edit_user_post"),
    path('<int:user_id>/delete', views.delete_user, name="delete_user"),
    
    path("login", views.login_user, name="login_user"),
    path("login_post", views.login_post, name="login_post"),
    path("logout", views.user_logout, name="logout"),
]