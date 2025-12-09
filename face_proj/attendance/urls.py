
from django.urls import path
from . import views
from .api import mark_attendance_api, attendance_list

app_name = 'attendance'

urlpatterns = [
    path('', views.home, name='home'),
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.student_add, name='student_add'),
    # path('attendance/', views.attendance_list, name='attendance_list'),


    path('run-face/', views.run_camera, name='run_camera'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("start-detection/", views.start_detection, name="start_detection"),

    path("", views.index),
    path("video_feed", views.video_feed),

    path('mark-attendance/', mark_attendance_api),
    path('attendance/', attendance_list),


]
 