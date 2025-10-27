# reservations/models.py
from django.db import models
from django.contrib.auth.models import User
from rooms.models import Room

def reservation_letter_upload_path(instance, filename):
    """
    Generate upload path for reservation letters based on admin type.
    Format: formal_letters/{admin_type_name}/{filename}
    """
    admin_type_name = instance.room.admin_type.name.lower().replace(' ', '_') if instance.room.admin_type else 'general'
    return f"formal_letters/{admin_type_name}/{filename}"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    # reason for reservation
    reason = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_note = models.TextField(blank=True, null=True)

    # generated letter file and timestamp
    letter_file = models.FileField(upload_to=reservation_letter_upload_path, null=True, blank=True)
    letter_generated_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username} - {self.room.name} ({self.date})"

    class Meta:
        ordering = ['-created_at']
