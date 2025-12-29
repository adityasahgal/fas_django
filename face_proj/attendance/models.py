from django.contrib.auth.models import User
import random
import string
from django.db import models

def generate_custom_id(size=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

class College(models.Model):
    college_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.name
class Program(models.Model):
    program_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
class Year(models.Model):
    year_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="years")
    year_number = models.PositiveIntegerField()  # 1, 2, 3, 4, etc.

    class Meta:
        unique_together = ('program', 'year_number')
        ordering = ['year_number']

    def __str__(self):
        return f"{self.program.name} - Year {self.year_number}"
class Semester(models.Model):
    semester_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="semesters")

    SEMESTER_CHOICES = [
        ("fall", "Fall"),
        ("spring", "Spring"),
        ("summer", "Summer"),
    ]
    name = models.CharField(max_length=20, choices=SEMESTER_CHOICES)
    order_number = models.PositiveIntegerField()  # 1, 2, 3

    class Meta:
        unique_together = ('year', 'name')
        ordering = ['order_number']

    def __str__(self):
        return f"{self.year} - {self.get_name_display()}"

class Course(models.Model):
    course_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="courses")
    code = models.CharField(max_length=20)  # ex: CS101
    title = models.CharField(max_length=200)
    credits = models.PositiveIntegerField(default=3)

    class Meta:
        unique_together = ('program', 'code')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title}"

# class Section(models.Model):
#     section_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
#     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
#     semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="sections")
#     section_number = models.CharField(max_length=10)  # A, B, C, etc.
#     instructor = models.CharField(max_length=200, blank=True)
#     schedule = models.CharField(max_length=200, blank=True)  # ex: MW 9:00–10:30
#     room = models.CharField(max_length=100, blank=True)

#     class Meta:
#         unique_together = ('course', 'semester', 'section_number')
#         ordering = ['course', 'section_number']

#     def __str__(self):
#         return f"{self.course.code} - Section {self.section_number} ({self.semester})"

class Section(models.Model):
    section_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name="sections")
    section_number = models.CharField(max_length=10)  # A, B, C, etc.

    subject = models.ForeignKey(
        "Subject",
        on_delete=models.CASCADE,
        related_name="sections",
        null=True, blank=True
    )

    instructor = models.ForeignKey(
        "Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sections"
    )

    schedule = models.CharField(max_length=200, blank=True)
    room = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ('course', 'semester', 'section_number')
        ordering = ['course', 'section_number']

    def __str__(self):
        return f"{self.course.code} - Section {self.section_number} ({self.semester})"
class Teacher(models.Model):
    teacher_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="teachers")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="teachers/photos/", null=True, blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class TeacherAttendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')
    lecture = models.ForeignKey(
        "Lecture",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_attendances"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('present','Present'),('absent','Absent')), default='present')
    source = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name} - {self.timestamp:%Y-%m-%d %H:%M:%S}"
class Camera(models.Model):
    camera_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="cameras")

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
class Subject(models.Model):
    subject_id = models.CharField(primary_key=True, max_length=8, unique=True, editable=False, default=generate_custom_id)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.course.code} - {self.name}"

class Student(models.Model):
    name = models.CharField(max_length=200)
    roll_no = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(
        "Course", 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name="students"
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )
    batch = models.CharField(max_length=50, blank=True, null=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    lecture = models.ForeignKey("Lecture", on_delete=models.CASCADE, null=True, blank=True, related_name="attendances")
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(('present','Present'),('absent','Absent')), default='present')
    source = models.CharField(max_length=100, blank=True, null=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.student} - {self.timestamp:%Y-%m-%d %H:%M:%S}"

class Lecture(models.Model):
    lecture_id = models.CharField(
        primary_key=True,
        max_length=8,
        default=generate_custom_id,
        editable=False,
        unique=True
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="lectures"
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="lectures"
    )

    date = models.DateField()
    time = models.TimeField()

    topic = models.CharField(max_length=255, blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('section', 'date', 'time')
        ordering = ['-date', '-time']

    def __str__(self):
        return f"{self.section} - {self.date} {self.time}"
