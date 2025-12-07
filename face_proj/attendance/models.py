
from django.db import models

# class Student(models.Model):
#     name = models.CharField(max_length=200)
#     roll_no = models.CharField(max_length=50, unique=True)
#     course = models.CharField(max_length=100, blank=True, null=True)
#     batch = models.CharField(max_length=50, blank=True, null=True)
#     photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.name} ({self.roll_no})"


# class Attendance(models.Model):
#     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
#     timestamp = models.DateTimeField(auto_now_add=True)
#     status = models.CharField(max_length=20, choices=(('present','Present'),('absent','Absent')), default='present')
#     source = models.CharField(max_length=100, blank=True, null=True)  # e.g., "camera1" or "manual"
#     note = models.TextField(blank=True, null=True)

#     class Meta:
#         ordering = ['-timestamp']

#     def __str__(self):
#         return f"{self.student} - {self.timestamp:%Y-%m-%d %H:%M:%S}"

class Course(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Semester(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # e.g., "Semester 1"

    def __str__(self):
        return f"{self.course.name} - {self.name}"

class Teacher(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to="teachers/photos/", null=True, blank=True)

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=200)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.semester})"

class Student(models.Model):
    name = models.CharField(max_length=200)
    roll_no = models.CharField(max_length=50, unique=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True)
    semester = models.ForeignKey(Semester, on_delete=models.SET_NULL, null=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.roll_no}"

class Lecture(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        unique_together = ('subject', 'date', 'start_time')

    def __str__(self):
        return f"{self.subject.name} - {self.date} {self.start_time}"

class Attendance(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE, related_name="attendances")
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, 
        choices=(('present', 'Present'), ('absent', 'Absent')),
        default='present'
    )

    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    source = models.CharField(max_length=100, blank=True, null=True)  # AI / Manual

    class Meta:
        unique_together = ('lecture', 'student')

    def __str__(self):
        return f"{self.student} → {self.lecture.subject} → {self.status}"

