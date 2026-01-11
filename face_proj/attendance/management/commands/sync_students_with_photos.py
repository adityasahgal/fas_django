import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from attendance.models import Student
import os
import mimetypes


class Command(BaseCommand):
    help = "Insert/Update students and save photos using student_id as filename"

    STUDENT_API = "https://erp.lloydcollege.in/services/erp/ai-attendance/get_students.php"
    PHOTO_API = "https://erp.lloydcollege.in/services/erp/ai-attendance/get_img_std.php"

    def handle(self, *args, **kwargs):
        response = requests.get(self.STUDENT_API, timeout=30)
        response.raise_for_status()
        students = response.json()

        for item in students:
            student, _ = Student.objects.update_or_create(
                uid=item.get("studentID"),
                defaults={
                    "school_id": item.get("school_id"),
                    "name": item.get("student_name"),
                    "class_name": item.get("class_name"),
                    "section_name": item.get("section_name"),
                    "semester_id": item.get("semester_id"),
                    "status": item.get("status", 1),
                }
            )

            # -------- PHOTO SECTION --------
            try:
                photo_api = f"{self.PHOTO_API}?student_id={student.uid}"
                photo_res = requests.get(photo_api, timeout=20)
                photo_res.raise_for_status()

                img_url = photo_res.json().get("img")
                if not img_url:
                    continue

                img_res = requests.get(img_url, timeout=20)
                img_res.raise_for_status()

                # Detect file extension
                content_type = img_res.headers.get("Content-Type")
                ext = mimetypes.guess_extension(content_type) or ".jpg"

                # Use student_id as filename
                filename = f"{student.uid}{ext}"

                student.photo.save(
                    filename,
                    ContentFile(img_res.content),
                    save=True
                )

                self.stdout.write(
                    self.style.SUCCESS(f"✔ Photo saved: {filename}")
                )

            except Exception as e:
                self.stderr.write(
                    self.style.WARNING(f"⚠ Photo failed for {student.uid}: {e}")
                )

        self.stdout.write(self.style.SUCCESS("🎉 Student sync completed"))