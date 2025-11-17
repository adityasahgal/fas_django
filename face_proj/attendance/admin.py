# attendance/admin.py
from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'roll_no', 'course', 'batch', 'created_at')
    search_fields = ('name', 'roll_no', 'course', 'batch')
    list_filter = ('course', 'batch')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'timestamp', 'status', 'source')
    list_filter = ('status', 'source')
    search_fields = ('student__name', 'student__roll_no')
    date_hierarchy = 'timestamp'
