import cv2
import os
import threading
import numpy as np
from deepface import DeepFace
from attendance.models import Student, Attendance
from django.utils.timezone import now
from datetime import timedelta

DATABASE_PATH = "media/students/photos"

CAM1 = "rtsp://admin:Admin%40123@192.168.1.250:554/cam/realmonitor?channel=1&subtype=0"
CAM2 = "rtsp://admin:Admin%40123@192.168.1.251:554/cam/realmonitor?channel=1&subtype=0"


from django.db import close_old_connections

def mark_attendance(matched_name, camera_name):
    # Ensure thread has a fresh DB connection
    close_old_connections()

    student = Student.objects.filter(name__icontains=matched_name).first()
    if not student:
        print(f"❌ Student not found: {matched_name}")
        return

    # today = now().date()

    # if Attendance.objects.filter(student=student, timestamp__date=today).exists():
    #     print(f"⏳ Already marked today → {student.name}")
    #     return
    
<<<<<<< HEAD
    ten_minutes_ago = now() - timedelta(minutes=10)
=======
    ten_minutes_ago = now() - timedelta(minutes=45)
>>>>>>> db5e040 (Upadte Models with its Relation)

    # Check if student already marked attendance within last 10 minutes
    if Attendance.objects.filter(student=student,
                                 timestamp__gte=ten_minutes_ago).exists():
        print(f"⏳ Already marked within 10 minutes → {student.name}")
        return

    Attendance.objects.create(
        student=student,
        status="present",
        source=f"AI-{camera_name}",
        timestamp=now()
    )
    print(f"✔ Marked: {student.name} from {camera_name}")


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

            result = DeepFace.find(
                img_path=img_array,
                db_path=DATABASE_PATH,
                enforce_detection=False
            )

            if isinstance(result, list) and len(result) > 0 and not result[0].empty:
                matched_file = os.path.basename(result[0].iloc[0]['identity'])
                matched_name = matched_file.split("_")[-1].split(".")[0]  # Abhishek

                print(f"🎯 Match on {camera_name}: {matched_name}")
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