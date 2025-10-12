from django.db import models
from django.core.validators import MinValueValidator

class Campus(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class AdminType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Room(models.Model):
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='rooms')
    admin_type = models.ForeignKey(AdminType, on_delete=models.SET_NULL, null=True, related_name='rooms')
    name = models.CharField(max_length=255)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.campus.name} - {self.name} (Cap: {self.capacity})"

    class Meta:
        unique_together = ['campus', 'name']
        ordering = ['campus', 'name']