from django.contrib import admin
from .models import Campus, AdminType, Room

@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at']
    search_fields = ['name', 'location']
    ordering = ['name']

@admin.register(AdminType)
class AdminTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'campus', 'admin_type', 'capacity', 'created_at']
    list_filter = ['campus', 'admin_type']
    search_fields = ['name', 'campus__name']
    ordering = ['campus', 'name']