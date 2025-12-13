import cv2
import os
import threading
import numpy as np
from deepface import DeepFace
from attendance.models import Student, Attendance, Teacher, TeacherAttendance, Lecture
from django.utils.timezone import now
from datetime import timedelta

DATABASE_PATH = "media/students/photos"

CAM1 = "rtsp://admin:Admin%40123@192.168.1.250:554/cam/realmonitor?channel=1&subtype=0"
CAM2 = "rtsp://admin:Admin%40123@192.168.1.251:554/cam/realmonitor?channel=1&subtype=0"


from django.db import close_old_connections

from datetime import time

def get_current_lecture_for_student(student):
    now_time = now().time()
    today = now().date()

    return Lecture.objects.filter(
        section=student.section,
        date=today,
        time__lte=now_time
    ).order_by('-time').first()

def get_current_lecture(teacher):
    now_time = now().time()
    today = now().date()

    return Lecture.objects.filter(
        teacher=teacher,
        date=today,
        time__lte=now_time
    ).order_by('-time').first()


def mark_student_attendance(student, camera_name):
    from django.utils.timezone import now
    today = now().date()
    
    if not student.section:
        print(f"❌ Student {student.roll_no} has no section assigned")
        return

    lecture = Lecture.objects.filter(section=student.section, date=today).order_by('-time').first()
    if not lecture:
        print("❌ No lecture found for section today")
        return

    # Check if attendance already marked
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        lecture=lecture,
        defaults={'status': 'present', 'source': camera_name}
    )

    if created:
        print(f"✅ Attendance marked for {student.name} ({student.roll_no})")
    else:
        print(f"⚠️ Attendance already marked for {student.name} ({student.roll_no})")


def mark_teacher_attendance(teacher, camera_name):
    ten_minutes_ago = now() - timedelta(minutes=45)

    if TeacherAttendance.objects.filter(
        teacher=teacher,
        timestamp__gte=ten_minutes_ago
    ).exists():
        print(f"⏳ Teacher already marked recently → {teacher.first_name}")
        return

    lecture = get_current_lecture(teacher)
    TeacherAttendance.objects.create(
        teacher=teacher,
        status="present",
        lecture=lecture,
        source=f"AI-{camera_name}"
    )
    print(f"✔ Teacher Marked: {teacher.first_name} {teacher.last_name} ({camera_name})")



def process_camera(camera_url, camera_name):
    print(f"📡 Opening {camera_name}...")
    cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)

    if not cap.isOpened():
        print(f"❌ Can't open: {camera_name}")
        return

    frame_skip = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"⚠ No frame from {camera_name}")
            break

        frame_skip += 1
        if frame_skip % 15 != 0:
            continue

        try:
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            # Encode frame to memory (avoids writing temp file)
            _, img_encoded = cv2.imencode('.jpg', small_frame)
            img_bytes = img_encoded.tobytes()

            img_array = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

            result_student = DeepFace.find(
                img_path=img_array,
                db_path="media/students/photos",
                enforce_detection=False
            )

            result_teacher = DeepFace.find(
                img_path=img_array,
                db_path="media/teachers/photos",
                enforce_detection=False
            )

            if isinstance(result_student, list) and len(result_student) > 0 and not result_student[0].empty:
                matched_file = os.path.basename(result_student[0].iloc[0]['identity'])
                matched_roll = os.path.splitext(matched_file)[0].split("_")[0]

                print(f"🎯 Student Match on {camera_name}: {matched_roll}")

                student = Student.objects.filter(roll_no__iexact=matched_roll).first()
                if student:
                    mark_student_attendance(student, camera_name)
                else:
                    print("❌ Student not found in DB")

                continue
 

            if isinstance(result_teacher, list) and len(result_teacher) > 0 and not result_teacher[0].empty:
                matched_file = os.path.basename(result_teacher[0].iloc[0]['identity'])
                name_part = os.path.splitext(matched_file)[0]

                first_name = name_part.split("_")[0]   # ✅ Abhishek

                print(f"🎯 Teacher Match on {camera_name}: {first_name}")

                teacher = Teacher.objects.filter(first_name__iexact=first_name).first()
                if teacher:
                    mark_teacher_attendance(teacher, camera_name)
                else:
                    print("❌ Teacher not found in DB")


        except Exception as e:
            print(f"⚠ Error {camera_name}: {e}")

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    print(f"🛑 Stopped {camera_name}")


def start_face_detection_parallel():
    print("🚀 Starting 2 Cameras in background...")

    t1 = threading.Thread(target=process_camera, args=(CAM1, "Camera-1"), daemon=True)
    t2 = threading.Thread(target=process_camera, args=(CAM2, "Camera-2"), daemon=True)

    t1.start()
    t2.start()

    print("✔ Both cameras running in background")