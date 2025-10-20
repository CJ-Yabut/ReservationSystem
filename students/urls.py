from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('profile/', views.view_profile, name='profile'),  # new profile view
]