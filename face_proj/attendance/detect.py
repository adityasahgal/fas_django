import cv2
import os
import threading
import numpy as np
from deepface import DeepFace
from attendance.models import Student, Attendance, Teacher, TeacherAttendance
from django.utils.timezone import now
from datetime import timedelta

DATABASE_PATH = "media/students/photos"

CAM1 = "rtsp://admin:Admin%40123@192.168.1.250:554/cam/realmonitor?channel=1&subtype=0"
CAM2 = "rtsp://admin:Admin%40123@192.168.1.251:554/cam/realmonitor?channel=1&subtype=0"


from django.db import close_old_connections

# def mark_attendance(matched_name, camera_name):
#     # Ensure thread has a fresh DB connection
#     close_old_connections()

#     student = Student.objects.filter(name__icontains=matched_name).first()
#     if not student:
#         print(f"❌ Student not found: {matched_name}")
#         return

#     # today = now().date()

#     # if Attendance.objects.filter(student=student, timestamp__date=today).exists():
#     #     print(f"⏳ Already marked today → {student.name}")
#     #     return
    
#     ten_minutes_ago = now() - timedelta(minutes=45)

#     # Check if student already marked attendance within last 10 minutes
#     if Attendance.objects.filter(student=student,
#                                  timestamp__gte=ten_minutes_ago).exists():
#         print(f"⏳ Already marked within 10 minutes → {student.name}")
#         return

#     Attendance.objects.create(
#         student=student,
#         status="present",
#         source=f"AI-{camera_name}",
#         timestamp=now()
#     )
#     print(f"✔ Marked: {student.name} from {camera_name}")

def mark_student_attendance(student, camera_name):
    ten_minutes_ago = now() - timedelta(minutes=45)

    if Attendance.objects.filter(student=student,
                                 timestamp__gte=ten_minutes_ago).exists():
        print(f"⏳ Student already marked recently → {student.name}")
        return

    Attendance.objects.create(
        student=student,
        status="present",
        source=f"AI-{camera_name}",
        timestamp=now()
    )
    print(f"✔ Student Marked: {student.name} ({camera_name})")

def mark_teacher_attendance(teacher, camera_name):
    ten_minutes_ago = now() - timedelta(minutes=45)

    if TeacherAttendance.objects.filter(
        teacher=teacher,
        timestamp__gte=ten_minutes_ago
    ).exists():
        print(f"⏳ Teacher already marked recently → {teacher.first_name}")
        return

    TeacherAttendance.objects.create(
        teacher=teacher,
        status="present",
        source=f"AI-{camera_name}",
        timestamp=now()
    )
    print(f"✔ Teacher Marked: {teacher.first_name} {teacher.last_name} ({camera_name})")

def mark_attendance(matched_name, camera_name):
    close_old_connections()

    # Student match
    student = Student.objects.filter(name__icontains=matched_name).first()
    if student:
        mark_student_attendance(student, camera_name)
        return

    # Teacher match
    teacher = Teacher.objects.filter(first_name__icontains=matched_name).first()
    if teacher:
        mark_teacher_attendance(teacher, camera_name)
        return

    print(f"❌ No student or teacher found for: {matched_name}")


# def process_camera(camera_url, camera_name):
#     print(f"📡 Opening {camera_name}...")
#     cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)

#     if not cap.isOpened():
#         print(f"❌ Can't open: {camera_name}")
#         return

#     frame_skip = 0

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print(f"⚠ No frame from {camera_name}")
#             break

#         frame_skip += 1
#         if frame_skip % 15 != 0:
#             continue

#         try:
#             # Resize for faster processing
#             small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

#             # Encode frame to memory (avoids writing temp file)
#             _, img_encoded = cv2.imencode('.jpg', small_frame)
#             img_bytes = img_encoded.tobytes()

#             # DeepFace can accept numpy array directly
#             img_array = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

#             result = DeepFace.find(
#                 img_path=img_array,
#                 db_path=DATABASE_PATH,
#                 enforce_detection=False
#             )

#             if isinstance(result, list) and len(result) > 0 and not result[0].empty:
#                 matched_file = os.path.basename(result[0].iloc[0]['identity'])
#                 # matched_name = matched_file.split("_")[-1].split(".")[0]  # Abhishek
#                 matched_name = os.path.splitext(matched_file)[0]
#                 matched_name = matched_name.replace("_", " ").strip()


#                 print(f"🎯 Match on {camera_name}: {matched_name}")
#                 mark_attendance(matched_name, camera_name)

#         except Exception as e:
#             print(f"⚠ Error {camera_name}: {e}")

#         if cv2.waitKey(1) == ord('q'):
#             break

#     cap.release()
#     print(f"🛑 Stopped {camera_name}")

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
            # Resize for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

            # Encode frame to memory (avoids writing temp file)
            _, img_encoded = cv2.imencode('.jpg', small_frame)
            img_bytes = img_encoded.tobytes()

            # DeepFace can accept numpy array directly
            img_array = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

            # STUDENT MATCH
            result_student = DeepFace.find(
                img_path=img_array,
                db_path="media/students/photos",
                enforce_detection=False
            )

            # TEACHER MATCH
            result_teacher = DeepFace.find(
                img_path=img_array,
                db_path="media/teachers/photos",
                enforce_detection=False
            )

            # Check Student
            if isinstance(result_student, list) and len(result_student) > 0 and not result_student[0].empty:
                matched_file = os.path.basename(result_student[0].iloc[0]['identity'])
                matched_name = os.path.splitext(matched_file)[0]
                if "_" in matched_name:
                    matched_name = matched_name.split("_", 1)[-1]  # only name part
                matched_name = matched_name.strip()
                print(f"🎯 Student Match on {camera_name}: {matched_name}")
                mark_attendance(matched_name, camera_name)
                continue  # Skip teacher check if student matched

            # Check Teacher
            if isinstance(result_teacher, list) and len(result_teacher) > 0 and not result_teacher[0].empty:
                matched_file = os.path.basename(result_teacher[0].iloc[0]['identity'])
                matched_name = os.path.splitext(matched_file)[0]
                if "_" in matched_name:
                    matched_name = matched_name.split("_", 1)[-1]  # only name part
                matched_name = matched_name.strip()
                print(f"🎯 Teacher Match on {camera_name}: {matched_name}")
                mark_attendance(matched_name, camera_name)

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