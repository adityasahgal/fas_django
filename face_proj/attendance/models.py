# attendance/models.py
from django.db import models

class Student(models.Model):
    name = models.CharField(max_length=200)
    roll_no = models.CharField(max_length=50, unique=True)
    course = models.CharField(max_length=100, blank=True, null=True)
    batch = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('present','Present'),('absent','Absent')), default='present')
    source = models.CharField(max_length=100, blank=True, null=True)  # e.g., "camera1" or "manual"
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student} - {self.timestamp:%Y-%m-%d %H:%M:%S}"
