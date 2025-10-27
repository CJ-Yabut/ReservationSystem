from django.db import models
from django.contrib.auth.models import User
from rooms.models import AdminType
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
import datetime

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
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, blank=True, null=True)

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
    

class Student(models.Model):
    DEPARTMENT_CHOICES = [
        ('Architecture', 'Architecture'),
        ('Chemical Engineer', 'Chemical Engineer'),
        ('Civil Engineer', 'Civil Engineer'),
        ('Computer Engineer', 'Computer Engineer'),
        ('Computer Science', 'Computer Science'),
        ('Electrical Engineer', 'Electrical Engineer'),
        ('Electronic Engineer', 'Electronic Engineer'),
        ('Industrial Engineer', 'Industrial Engineer'),
        ('Information Technology', 'Information Technology'),
        ('Mechanical Engineer', 'Mechanical Engineer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    profile_picture = models.FileField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.username})"
