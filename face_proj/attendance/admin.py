from django.contrib import admin
from .models import Student, Attendance, Teacher, Camera
from import_export.admin import ImportExportModelAdmin
from .resources import StudentResource, AttendanceResource


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('uid', 'name')

@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = StudentResource
    list_display = ('school_id', 'uid', 'name', 'class_name', 'section_name', 'semester_id', 'photo', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'school_id', 'created_at')
    search_fields = ('school_id', 'uid', 'name', 'class_name', 'section_name', 'semester_id', 'photo', 'status', 'created_at', 'updated_at')

@admin.register(Attendance)
class AttendanceAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_class = AttendanceResource
    list_display = ('uid', 'name', 'lecture_no', 'status', 'source', 'created_at')
    list_filter = ('status', 'source', 'created_at')
    search_fields = ('name',)
@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = (
        'camera_id',
        'location',
        'ip_address',
        'rtsp_port',
        'is_online',
        'last_checked'
    )

    list_filter = ('is_online', 'supports_ptz')
    search_fields = ('camera_id', 'location', 'ip_address')
    readonly_fields = ('camera_id',)

    fieldsets = (
        ("Basic Info", {
            "fields": ("camera_id", "location", "description")
        }),
        ("Network Configuration", {
            "fields": ("ip_address", "port", "rtsp_port")
        }),
        ("Authentication", {
            "fields": ("username", "password")
        }),
        ("Stream URLs", {
            "fields": ("rtsp_url", "snapshot_url")
        }),
        ("Camera Details", {
            "fields": ("model_number", "firmware_version", "supports_ptz")
        }),
        ("Status", {
            "fields": ("is_online", "last_checked")
        }),
    )