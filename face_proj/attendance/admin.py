from django.contrib import admin
from .models import Course, Section, Semester, Student, Attendance, College, Program, Year

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('college_id', 'name', 'email', 'phone', 'city', 'state', 'country')
    search_fields = ('name', 'email', 'phone', 'city', 'state', 'country')
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'name', 'college')
    search_fields = ('name', 'college__name')

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    list_display = ('year_id', 'program', 'year_number')
    search_fields = ('program__name',)

@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    list_display = ('semester_id', 'year', 'name')
    search_fields = ('year__program__name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'code', 'title', 'program')
    search_fields = ('code', 'title', 'program__name')

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('section_id', 'course', 'semester', 'section_number', 'instructor')
    search_fields = ('course__code', 'semester__name', 'section_number', 'instructor')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'roll_no', 'course', 'batch')
    search_fields = ('name', 'roll_no', 'course', 'batch')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'status', 'source', 'timestamp')
    list_filter = ('status', 'source', 'timestamp')
    search_fields = ('student__name',)
