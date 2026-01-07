from django.urls import path
from . import views

urlpatterns = [
    # Admin Dashboard & Exam Management
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/exams/', views.exam_list_admin, name='exam_list_admin'),
    path('admin/exams/create/', views.create_exam, name='create_exam'),
    path('admin/exams/<int:exam_id>/', views.exam_detail_admin, name='exam_detail_admin'),
    path('admin/exams/<int:exam_id>/update/', views.update_exam, name='update_exam'),
    path('admin/exams/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    
    # Grading
    path('admin/submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    
    # Student Dashboard & Exams
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/exams/', views.exam_list_student, name='exam_list_student'),
    path('student/exams/<int:exam_id>/', views.exam_detail_student, name='exam_detail_student'),
    path('student/exams/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
    
    # Results
    path('student/results/', views.view_results, name='view_results'),
]