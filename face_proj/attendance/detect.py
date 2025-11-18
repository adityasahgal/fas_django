import cv2
import os
from deepface import DeepFace
from attendance.models import Student, Attendance

# Student images folder
DATABASE_PATH = "media/students/photos"

def start_face_detection():
    cap = cv2.VideoCapture(0)

    print("📷 Camera Started... Looking for face...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        try:
            result = DeepFace.find(
                img_path=frame,
                db_path=DATABASE_PATH,
                enforce_detection=False
            )

            if isinstance(result, list) and len(result) > 0 and not result[0].empty:
                matched_file = os.path.basename(result[0].iloc[0]['identity'])
                matched_name = matched_file.split(".")[0]

                print("🎉 Face Recognized:", matched_name)

                # DB search
                student = Student.objects.filter(name__icontains=matched_name).first()
                
                if student:
                    # Check if already marked today
                    if not Attendance.objects.filter(student=student).exists():
                        Attendance.objects.create(student=student, status="present", source="AI")
                        print("✔ Attendance Marked for:", student.name)
                    else:
                        print("⏳ Already Marked Today.")

        except Exception as e:
            print("⚠ Face recognition error:", e)

        cv2.imshow("Scanner", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
