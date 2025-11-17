# scripts/import_old_db.py
import sqlite3
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_proj.settings')
django.setup()

from attendance.models import Student, Attendance
conn = sqlite3.connect('/path/to/attendance.db')  # path to your old DB
cur = conn.cursor()

# Inspect tables
print("Tables:", cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall())

# Example: if old table is `students` with columns id,name,roll_no,course,batch,photo
for row in cur.execute("SELECT id, name, roll_no, course, batch, photo FROM students"):
    _id, name, roll, course, batch, photo = row
    Student.objects.update_or_create(roll_no=roll, defaults={'name': name, 'course': course, 'batch': batch})

# Example attendance import
for row in cur.execute("SELECT student_id, timestamp, status FROM attendance"):
    student_id, ts, status = row
    # map student_id (old id) to Student object via roll or maintain a mapping
    # If old DB stored roll_no in attendance table, use it; otherwise create mapping table while importing students.
    # Example assuming old table has roll_no:
    # Student.objects.get(roll_no=...)
    # Attendance.objects.create(student=..., timestamp=..., status=status)
