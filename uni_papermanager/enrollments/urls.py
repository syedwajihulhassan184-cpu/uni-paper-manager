from django.urls import path
from . import views

urlpatterns = [
    # Student Enrollment Management
    path('my-enrollments/', views.my_enrollments, name='my_enrollments'),
    path('available-courses/', views.available_courses, name='available_courses'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('unenroll/<int:enrollment_id>/', views.unenroll_course, name='unenroll_course'),
    path('enrollments/<int:enrollment_id>/', views.enrollment_detail, name='enrollment_detail'),
    
    # Admin Enrollment Management
    path('admin/enrollments/', views.manage_enrollments, name='manage_enrollments'),
    path('admin/courses/<int:course_id>/enrollments/', views.course_enrollments, name='course_enrollments'),
    path('admin/students/<int:student_id>/enrollments/', views.student_enrollments_admin, name='student_enrollments_admin'),
    path('admin/courses/<int:course_id>/bulk-enroll/', views.bulk_enroll, name='bulk_enroll'),
    path('admin/enrollments/<int:enrollment_id>/delete/', views.delete_enrollment_admin, name='delete_enrollment_admin'),
]