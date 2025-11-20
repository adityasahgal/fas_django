from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'roll_no', 'course', 'batch')
    search_fields = ('name', 'roll_no', 'course', 'batch')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'status', 'source', 'timestamp')
    list_filter = ('status', 'source', 'timestamp')
    search_fields = ('student__name',)
