from import_export import resources
from .models import Student, Attendance, College

class StudentResource(resources.ModelResource):
    class Meta:
        model = Student
        fields = ('id', 'name', 'roll_no', 'course', 'batch')  # columns in export
        export_order = ('id', 'name', 'roll_no', 'course', 'batch')

class AttendanceResource(resources.ModelResource):
    class Meta:
        model = Attendance
        fields = ('id', 'student__name', 'status', 'source', 'timestamp')
        export_order = ('id', 'student__name', 'status', 'source', 'timestamp')


class CollegeResource(resources.ModelResource):
    class Meta:
        model = College
        fields = ('college_id', 'name', 'email', 'phone', 'city', 'state', 'country')
        export_order = ('college_id', 'name', 'email', 'phone', 'city', 'state', 'country')
