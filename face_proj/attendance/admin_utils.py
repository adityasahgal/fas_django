# attendance/admin_utils.py
import csv
from io import BytesIO, StringIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def export_attendance_csv(queryset, filename="attendance_export.csv"):
    """
    Accepts a queryset of Attendance objects or a list-of-dicts and returns HttpResponse with CSV.
    If queryset is Attendance queryset, we will map fields automatically.
    """
    # Build CSV in memory
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Session ID", "Session Subject", "Classroom", "Teacher",
        "Student ID", "Student Name", "Roll No", "Status", "Marked At"
    ])

    for att in queryset:
        writer.writerow([
            getattr(att.session, 'session_id', ''),
            getattr(att.session, 'subject', ''),
            getattr(att.session, 'classroom', ''),
            getattr(att.session, 'teacher', ''),
            getattr(att.student, 'student_id', ''),
            getattr(att.student, 'name', ''),
            getattr(att.student, 'roll_no', ''),
            att.status,
            att.marked_at.strftime("%Y-%m-%d %H:%M:%S") if att.marked_at else ''
        ])

    resp = HttpResponse(output.getvalue(), content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


def export_attendance_pdf(queryset, filename="attendance_export.pdf"):
    """
    Create a basic PDF with table rows from Attendance queryset.
    Uses reportlab.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    title = Paragraph("Attendance Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))

    # Table header
    data = [[
        "Session ID", "Subject", "Classroom", "Teacher",
        "Student ID", "Student Name", "Roll No", "Status", "Marked At"
    ]]

    # Rows
    for att in queryset:
        data.append([
            getattr(att.session, 'session_id', ''),
            getattr(att.session, 'subject', ''),
            str(getattr(att.session, 'classroom', '')),
            str(getattr(att.session, 'teacher', '')),
            getattr(att.student, 'student_id', ''),
            getattr(att.student, 'name', ''),
            getattr(att.student, 'roll_no', ''),
            att.status,
            att.marked_at.strftime("%Y-%m-%d %H:%M:%S") if att.marked_at else ''
        ])

    # Create a table and style it
    table = Table(data, repeatRows=1)
    tbl_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#d3d3d3")),
        ('GRID', (0,0), (-1,-1), 0.25, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
    ])
    table.setStyle(tbl_style)
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    resp = HttpResponse(buffer.read(), content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp
