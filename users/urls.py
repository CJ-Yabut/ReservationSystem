from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('register/', views.student_register, name='student_register'),
    path('admin/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
]