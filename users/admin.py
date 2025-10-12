from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'admin_type', 'created_at']
    list_filter = ['role', 'admin_type']
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']