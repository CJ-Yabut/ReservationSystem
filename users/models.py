from django.db import models
from django.contrib.auth.models import User
from rooms.models import AdminType
from django.utils import timezone
from datetime import timedelta

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


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    email = models.EmailField()
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_valid(self):
        """Check if token is still valid (within 10 minutes)"""
        expiry_time = self.created_at + timedelta(minutes=10)
        return timezone.now() < expiry_time
    
    def __str__(self):
        return f"{self.email} - {self.verification_code}"