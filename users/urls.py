from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', views.student_login, name='student_login'),
    path('register/', views.student_register, name='student_register'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('admin/', views.admin_login, name='admin_login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.student_dashboard, name='student_dashboard'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='students/change_password.html'), name='change_password'),
    path('password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='students/password_change_done.html'), name='password_change_done'),
    path('verify-email/', views.verify_email, name='verify_email'),

]
