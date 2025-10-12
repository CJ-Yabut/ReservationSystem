from django.db import models
from django.contrib.auth.models import User
from rooms.models import AdminType

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
        ('superadmin', 'Superadmin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    admin_type = models.ForeignKey(AdminType, on_delete=models.SET_NULL, null=True, blank=True, related_name='admins')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    class Meta:
        ordering = ['user__username']