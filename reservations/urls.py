from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_room, name='book_room'),
    path('student/reservations/', views.student_reservations, name='student_reservations'),
    path('student/cancel/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('admin/reservations/', views.manage_reservations, name='manage_reservations'),
    path('admin/approve/<int:reservation_id>/', views.approve_reservation, name='approve_reservation'),
    path('admin/reject/<int:reservation_id>/', views.reject_reservation, name='reject_reservation'),
]