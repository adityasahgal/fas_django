from django.contrib.auth.models import User
import random
import string
from django.db import models

def generate_custom_id(size=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

class Teacher(models.Model):
    school_id = models.IntegerField(null=True, blank=True)
    uid = models.IntegerField(unique=True)
    card_no = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    class_name = models.TextField(null=True, blank=True)
    section_name = models.TextField(null=True, blank=True)
    semester_id = models.IntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to="students/photos/", null=True, blank=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or str(self.uid)
        
class Camera(models.Model):
    camera_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    # Basic Info
    location = models.CharField(max_length=255)           # e.g., "Classroom 101"
    description = models.TextField(blank=True, null=True)

    # Network Config
    ip_address = models.GenericIPAddressField()            # IP Address of the camera
    port = models.PositiveIntegerField(default=80)         # Default HTTP port (80 or others)
    rtsp_port = models.PositiveIntegerField(default=554)   # RTSP streaming port

    # Authentication
    username = models.CharField(max_length=100, default='admin')
    password = models.CharField(max_length=100)             # Store securely in production (encrypted or environment variables)

    # Stream URLs
    rtsp_url = models.CharField(max_length=255, blank=True, null=True)  # RTSP stream URL if custom
    snapshot_url = models.CharField(max_length=255, blank=True, null=True)  # Snapshot URL to capture images

    # Camera Model & Capabilities
    model_number = models.CharField(max_length=100, blank=True, null=True) 
    firmware_version = models.CharField(max_length=100, blank=True, null=True)
    supports_ptz = models.BooleanField(default=False)       # Pan-Tilt-Zoom

    # Status info (optional - updated by monitoring routine)
    is_online = models.BooleanField(default=False)
    last_checked = models.DateTimeField(blank=True, null=True)

    def _str_(self):
        return f"{self.location} ({self.ip_address})"

class Student(models.Model):
    school_id = models.IntegerField(null=True, blank=True)
    uid = models.IntegerField(unique=True)
    card_no = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    class_name = models.TextField(null=True, blank=True)
    section_name = models.TextField(null=True, blank=True)
    semester_id = models.IntegerField(null=True, blank=True)
    photo = models.ImageField(upload_to="students/photos/", null=True, blank=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "students"

    def _str_(self):
        return self.name or str(self.uid)
class Attendance(models.Model):
    type = models.CharField(max_length=20, choices=(('student','Student'),('teacher','Teacher')), default='student')
    uid = models.IntegerField(null=True, blank=True)
    school_id = models.IntegerField(null=True, blank=True)
    card_no = models.TextField(null=True, blank=True)
    name = models.TextField(null=True, blank=True)
    class_name = models.TextField(null=True, blank=True)
    section_name = models.TextField(null=True, blank=True)
    semester_id = models.IntegerField(null=True, blank=True)
    lecture_no = models.IntegerField(null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=(('present','Present'),('absent','Absent')), default='present')
    source = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at:%Y-%m-%d %H:%M:%S}"