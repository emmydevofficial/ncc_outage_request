from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_requests, name="all_requests"),
    path('add_request', views.add_request, name="add_request"),
    path('reviwed_request', views.all_reviewed_requests, name="all_reviewed_requests"),
    path('approved_request', views.all_approved_requests, name="all_approved_requests"),
    path('create_request', views.create_request, name="create_request"),
    path('logs', views.activity_logs, name='activity_logs'),
    path('logs/<str:request_id>', views.activity_logs, name='activity_logs'),
    path('<int:request_id>/edit', views.edit_request, name='edit_request'),
    path('<int:request_id>/execute', views.confirm_execution, name='confirm_execution'),
    
    path('<int:request_id>/view', views.view_request, name="view_request"),
    path('<int:request_id>/review', views.review_request, name="review_request"),
    path('<int:request_id>/review_post', views.review_request_post, name="review_request_post"),
    path('<int:request_id>/approve', views.approve_request, name="approve_request"),
    path('<int:request_id>/approve_post', views.approve_request_post, name="approve_request_post"),
    
    path('generate-request-report/<int:request_id>/', views.generate_request_report, name='generate_request_report'),
    
    path("get_approved_date", views.get_approved_date, name="get_approved_date"),
]