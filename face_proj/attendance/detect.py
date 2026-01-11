import cv2
import os
import threading
from datetime import datetime, date, time, timedelta

from deepface import DeepFace
from django.db import close_old_connections
from django.utils.timezone import localtime, make_aware

from attendance.models import Student, Teacher, Attendance

# =====================================================
# DATABASE PATHS
# =====================================================
STUDENT_DB = "media/students/photos"
TEACHER_DB = "media/teachers/photos"

# =====================================================
# CP PLUS RTSP (SUB STREAM)
# =====================================================
CAM1 = "rtsp://admin:Admin%40123@192.168.1.250:554/cam/realmonitor?channel=1&subtype=1"
CAM2 = "rtsp://admin:Admin%40123@192.168.1.251:554/cam/realmonitor?channel=1&subtype=1"

# =====================================================
# LECTURE CONFIG
# =====================================================
LECTURE_START_TIME = time(0, 0)
LECTURE_END_TIME   = time(23, 59)
LECTURE_DURATION   = 45  # minutes

# =====================================================
# FACE MATCH THRESHOLDS
# =====================================================
STUDENT_THRESHOLD = 0.35
TEACHER_THRESHOLD = 0.35

# =====================================================
# LIVE MESSAGE
# =====================================================
last_message = ""
last_message_time = None
MESSAGE_DURATION = 3
message_lock = threading.Lock()

# =====================================================
# GLOBAL ARC FACE MODEL (LOAD ONCE)
# =====================================================
arcface_model = None
model_lock = threading.Lock()


def load_arcface_once():
    global arcface_model
    with model_lock:
        if arcface_model is None:
            print("✅ Loading ArcFace model (ONE TIME)...")
            arcface_model = DeepFace.build_model("ArcFace")


# =====================================================
def get_current_lecture_slot():
    current = localtime()
    today = current.date()

    start_dt = make_aware(datetime.combine(today, LECTURE_START_TIME))
    end_dt   = make_aware(datetime.combine(today, LECTURE_END_TIME))

    if current < start_dt or current >= end_dt:
        return None

    elapsed = int((current - start_dt).total_seconds() // 60)
    lecture_no = (elapsed // LECTURE_DURATION) + 1

    lecture_start = start_dt + timedelta(minutes=(lecture_no - 1) * LECTURE_DURATION)
    lecture_end   = lecture_start + timedelta(minutes=LECTURE_DURATION)

    return {
        "lecture_no": lecture_no,
        "start": lecture_start.time(),
        "end": lecture_end.time(),
    }


# =====================================================
def mark_attendance(person, user_type, camera_name):
    global last_message, last_message_time
    close_old_connections()

    slot = get_current_lecture_slot()
    if not slot:
        return

    today = date.today()
    lecture_no = slot["lecture_no"]

    if Attendance.objects.filter(
        uid=person.uid,
        type=user_type,
        date=today,
        lecture_no=lecture_no
    ).exists():
        return

    Attendance.objects.create(
        type=user_type,
        uid=person.uid,
        name=person.name,
        lecture_no=lecture_no,
        date=today,
        start_time=slot["start"],
        end_time=slot["end"],
        status="present",
        source=camera_name,
        note="CP Plus AI Face Match"
    )

    with message_lock:
        last_message = f"{user_type.upper()} MATCHED: {person.name} | Lecture {lecture_no}"
        last_message_time = datetime.now()

    print("✅ ATTENDANCE MARKED:", last_message)


# =====================================================
def process_camera(camera_url, camera_name):
    close_old_connections()
    print(f"\n📡 Opening {camera_name}")

    load_arcface_once()  # SAFE CALL

    cap = cv2.VideoCapture(camera_url, cv2.CAP_FFMPEG)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

    if not cap.isOpened():
        print("❌ Camera not opened:", camera_name)
        return

    frame_no = 0

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue

        frame_no += 1
        frame = cv2.resize(frame, (640, 480))

        # LIVE MESSAGE
        msg = "Detecting face..."
        with message_lock:
            if last_message and last_message_time:
                if (datetime.now() - last_message_time).seconds <= MESSAGE_DURATION:
                    msg = last_message

        cv2.putText(frame, msg, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow(camera_name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if frame_no % 20 != 0:
            continue

        if not get_current_lecture_slot():
            continue

        try:
            faces = DeepFace.extract_faces(
                img_path=frame,
                detector_backend="opencv",
                enforce_detection=False
            )

            for f in faces:
                face_img = f["face"]

                # ================= STUDENT =================
                students = DeepFace.find(
                    img_path=face_img,
                    db_path=STUDENT_DB,
                    model_name="ArcFace",
                    detector_backend="opencv",
                    distance_metric="cosine",
                    enforce_detection=False,
                    silent=True
                )

                if students and not students[0].empty:
                    best = students[0].iloc[0]
                    if best["distance"] < STUDENT_THRESHOLD:
                        uid = os.path.splitext(os.path.basename(best["identity"]))[0]
                        student = Student.objects.filter(uid=uid).first()
                        if student:
                            mark_attendance(student, "student", camera_name)
                            break

                # ================= TEACHER =================
                teachers = DeepFace.find(
                    img_path=face_img,
                    db_path=TEACHER_DB,
                    model_name="ArcFace",
                    detector_backend="opencv",
                    distance_metric="cosine",
                    enforce_detection=False,
                    silent=True
                )

                if teachers and not teachers[0].empty:
                    best = teachers[0].iloc[0]
                    if best["distance"] < TEACHER_THRESHOLD:
                        name = os.path.splitext(os.path.basename(best["identity"]))[0]
                        teacher = Teacher.objects.filter(name__iexact=name).first()
                        if teacher:
                            mark_attendance(teacher, "teacher", camera_name)
                            break

        except Exception as e:
            print("❌ Detection Error:", e)

    cap.release()
    cv2.destroyAllWindows()


# =====================================================
def start_face_detection_parallel():
    print("🚀 CP PLUS FACE ATTENDANCE SYSTEM STARTED")

    threading.Thread(
        target=process_camera,
        args=(CAM1, "CPPlus-Cam-1"),
        daemon=True
    ).start()

    threading.Thread(
        target=process_camera,
        args=(CAM2, "CPPlus-Cam-2"),
        daemon=True
    ).start()
