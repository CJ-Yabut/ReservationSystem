from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('admin/panel/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('rooms.urls')),
    path('', include('reservations.urls')),
]