from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import timedelta
from django.db import close_old_connections
from .models import Attendance, Student
from .serializers import AttendanceSerializer

@api_view(['GET'])
def attendance_list(request):
    records = Attendance.objects.all()
    serializer = AttendanceSerializer(records, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def mark_attendance_api(request):
    matched_name = request.data.get('matched_name')
    camera_name = request.data.get('camera_name')

    if not matched_name:
        return Response({"error": "matched_name is required"}, status=400)

    # Ensure thread-safe connection
    close_old_connections()

    student = Student.objects.filter(name__icontains=matched_name).first()
    if not student:
        return Response({"error": "Student not found"}, status=404)

    ten_minutes_ago = now() - timedelta(minutes=45)

    already = Attendance.objects.filter(
        student=student,
        timestamp__gte=ten_minutes_ago
    ).exists()

    if already:
        return Response({"message": "Already marked recently"}, status=200)

    Attendance.objects.create(
        student=student,
        status="present",
        source=f"AI-{camera_name}",
        timestamp=now()
    )

    return Response({"message": "Attendance marked", "student": student.name})
