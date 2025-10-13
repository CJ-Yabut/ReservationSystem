from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('register/', views.student_register, name='student_register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('admin/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
]