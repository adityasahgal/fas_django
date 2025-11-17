# attendance/management/commands/run_detect.py
from django.core.management.base import BaseCommand
import time
from attendance.detect import recognize_loop  # we'll wrap your existing detection entry point
from attendance.models import Student, Attendance

class Command(BaseCommand):
    help = 'Run face detection/recognition loop and create attendance records'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting detection loop (CTRL+C to stop)"))
        try:
            # assume detect.py provides a function that yields recognized roll_no/name
            # We'll show an example wrapper — adapt to your detect.py interface
            for recognized in recognize_loop():
                # recognized is expected to be a dict: {'roll_no': '123', 'name':'Aditya', 'confidence':0.8}
                roll_no = recognized.get('roll_no') or recognized.get('name')
                if not roll_no:
                    continue
                try:
                    student = Student.objects.get(roll_no=roll_no)
                except Student.DoesNotExist:
                    # Optionally create a placeholder student, or skip
                    self.stdout.write(f"Unknown student recognized: {roll_no}")
                    continue
                Attendance.objects.create(student=student, status='present', source='camera1')
                self.stdout.write(self.style.SUCCESS(f"Marked present: {student}"))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("Detection loop stopped"))
