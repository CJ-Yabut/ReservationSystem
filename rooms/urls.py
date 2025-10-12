from django.urls import path
from . import views

urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add-room/', views.add_room, name='add_room'),
    path('admin/edit-room/<int:room_id>/', views.edit_room, name='edit_room'),
    path('admin/delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('calendar/<int:room_id>/', views.room_calendar, name='room_calendar'),
]