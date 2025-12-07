from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Attendance
from django import forms
from django.http import JsonResponse, HttpResponse

from django.http import StreamingHttpResponse
from django.shortcuts import render
import cv2
from attendance.detect import start_face_detection_parallel
import threading



def index(request):
    return render(request, "camera.html")

def gen_frames():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  

    while True:
        success, frame = cap.read()
        if not success:
            break

        
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


from attendance.streamer import start_hls_stream
CAM1 = "rtsp://admin:Admin%40123@192.168.1.250:554/cam/realmonitor?channel=1&subtype=0"
CAM2 = "rtsp://admin:Admin%40123@192.168.1.251:554/cam/realmonitor?channel=1&subtype=0"

def run_camera(request):
    t1 = threading.Thread(target=start_hls_stream, args=(CAM1, "cam1"))
    t2 = threading.Thread(target=start_hls_stream, args=(CAM2, "cam2"))

    t1.start()
    t2.start()

    return JsonResponse({"message": "IP Camera Streams Started"})


def start_detection(request):
    start_face_detection_parallel()
    return HttpResponse("🔥 Face detection started on both cameras")

def dashboard(request):
    return render(request, "attendance/dashboard.html")


