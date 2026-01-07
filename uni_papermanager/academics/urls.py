from django.urls import path
from . import views

urlpatterns = [
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:department_id>/', views.department_detail, name='department_detail'),
    path('departments/create/', views.create_department, name='create_department'),
    path('departments/<int:department_id>/update/', views.update_department, name='update_department'),
    
    # Programs
    path('programs/', views.program_list, name='program_list'),
    path('programs/<int:program_id>/', views.program_detail, name='program_detail'),
    path('programs/create/', views.create_program, name='create_program'),
    path('programs/<int:program_id>/update/', views.update_program, name='update_program'),
    
    # Courses
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:course_id>/update/', views.update_course, name='update_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),
    path('courses/bulk-create/',views.bulk_create_courses,name='bulk_create_courses')
]