from import_export import resources
from .models import Student, Attendance

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('uid', 'name')  # columns in export
        export_order = ('uid', 'name')

class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance
        fields = ('uid', 'name', 'status', 'source', 'created_at')
        export_order = ('uid', 'name', 'status', 'source', 'created_at')

