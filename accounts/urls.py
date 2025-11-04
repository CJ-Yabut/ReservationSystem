from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ...existing urls...
    path('my-profile/photo/', views.profile_photo_view, name='profile_photo'),
]
