from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'date', 'start_time', 'end_time', 'status', 'created_at']
    list_filter = ['status', 'date', 'room__campus']
    search_fields = ['student__username', 'room__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']