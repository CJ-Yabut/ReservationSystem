from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='login/', permanent=False)),
    path('admin/panel/', admin.site.urls),
    path('', include('users.urls', namespace='users')),
    path('', include('rooms.urls')),
    path('', include(('reservations.urls', 'reservations'), namespace='reservations')),
    path('students/', include('students.urls')),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
