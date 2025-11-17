# attendance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Attendance
from django import forms
from django.http import JsonResponse
from attendance.detect import start_face_detection

from django.http import StreamingHttpResponse
from django.shortcuts import render
import cv2

def index(request):
    return render(request, "camera.html")

def gen_frames():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Windows Fix

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Draw rectangle example (later replace with recognition)
        cv2.putText(frame, "Camera Working", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        _, buffer = cv2.imencode(".jpg", frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def video_feed(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_no', 'course', 'batch', 'photo']

def home(request):
    recent = Attendance.objects.select_related('student').all()[:20]
    return render(request, 'attendance/home.html', {'recent': recent})

def student_list(request):
    students = Student.objects.all()
    return render(request, 'attendance/student_list.html', {'students': students})

def student_add(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('attendance:student_list')
    else:
        form = StudentForm()
    return render(request, 'attendance/student_form.html', {'form': form})

def attendance_list(request):
    qs = Attendance.objects.select_related('student').all()[:200]
    return render(request, 'attendance/attendance_list.html', {'attendances': qs})

def run_camera(request):
    start_face_detection()
    return JsonResponse({"message": "Camera Closed — Attendance Updated"})
