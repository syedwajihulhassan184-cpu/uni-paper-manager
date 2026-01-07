from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Department, Program, Course
from .forms import (
    DepartmentForm, ProgramForm, CourseForm,
    CourseFilterForm, ProgramFilterForm, BulkCourseCreateForm
)
from enrollments.models import Enrollment
from exams.models import Exam

# Department Views

@login_required
def department_list(request):
    """List all departments"""
    departments = Department.objects.annotate(
        program_count=Count('program')
    ).all()
    
    context = {
        'departments': departments
    }
    return render(request, 'academics/department_list.html', context)


@login_required
def department_detail(request, department_id):
    """View department details with programs"""
    department = get_object_or_404(Department, department_id=department_id)
    programs = Program.objects.filter(department=department).annotate(
        course_count=Count('course')
    )
    
    context = {
        'department': department,
        'programs': programs
    }
    return render(request, 'academics/department_detail.html', context)


@login_required
def create_department(request):
    """Create new department - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can create departments')
        return redirect('department_list')
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully')
            return redirect('department_list')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = DepartmentForm()
    
    return render(request, 'academics/create_department.html', {'form': form})


@login_required
def update_department(request, department_id):
    """Update department - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can update departments')
        return redirect('department_list')
    
    department = get_object_or_404(Department, department_id=department_id)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully')
            return redirect('department_detail', department_id=department_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = DepartmentForm(instance=department)
    
    context = {'form': form, 'department': department}
    return render(request, 'academics/update_department.html', context)


# Program Views

@login_required
def program_list(request):
    """List all programs"""
    programs = Program.objects.select_related('department').annotate(
        course_count=Count('course')
    ).all()
    
    # Apply filter
    filter_form = ProgramFilterForm(request.GET)
    if filter_form.is_valid():
        department = filter_form.cleaned_data.get('department')
        if department:
            programs = programs.filter(department=department)
    
    context = {
        'programs': programs,
        'filter_form': filter_form
    }
    return render(request, 'academics/program_list.html', context)


@login_required
def program_detail(request, program_id):
    """View program details with courses"""
    program = get_object_or_404(
        Program.objects.select_related('department'),
        program_id=program_id
    )
    courses = Course.objects.filter(program=program).annotate(
        exam_count=Count('exam')
    )
    
    # If student, show enrollment status
    enrolled_courses = []
    if request.user.user_type == 'student':
        student = request.user.student
        enrolled_courses = list(
            Enrollment.objects.filter(student=student)
            .values_list('course_id', flat=True)
        )
    
    context = {
        'program': program,
        'courses': courses,
        'enrolled_courses': enrolled_courses
    }
    return render(request, 'academics/program_detail.html', context)


@login_required
def create_program(request):
    """Create new program - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can create programs')
        return redirect('program_list')
    
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Program created successfully')
            return redirect('program_list')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ProgramForm()
    
    return render(request, 'academics/create_program.html', {'form': form})


@login_required
def update_program(request, program_id):
    """Update program - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can update programs')
        return redirect('program_list')
    
    program = get_object_or_404(Program, program_id=program_id)
    
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Program updated successfully')
            return redirect('program_detail', program_id=program_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ProgramForm(instance=program)
    
    context = {'form': form, 'program': program}
    return render(request, 'academics/update_program.html', context)


# Course Views

@login_required
def course_list(request):
    """List all courses"""
    courses = Course.objects.select_related(
        'program__department'
    ).annotate(
        exam_count=Count('exam')
    ).all()
    
    # Apply filters
    filter_form = CourseFilterForm(request.GET)
    if filter_form.is_valid():
        department = filter_form.cleaned_data.get('department')
        program = filter_form.cleaned_data.get('program')
        
        if department:
            courses = courses.filter(program__department=department)
        if program:
            courses = courses.filter(program=program)
    
    # If student, show enrollment status
    enrolled_courses = []
    if request.user.user_type == 'student':
        student = request.user.student
        enrolled_courses = list(
            Enrollment.objects.filter(student=student)
            .values_list('course_id', flat=True)
        )
    
    context = {
        'courses': courses,
        'filter_form': filter_form,
        'enrolled_courses': enrolled_courses
    }
    return render(request, 'academics/course_list.html', context)


@login_required
def course_detail(request, course_id):
    """View course details with exams"""
    course = get_object_or_404(
        Course.objects.select_related('program__department'),
        course_id=course_id
    )
    
    # Get exams for this course
    exams = Exam.objects.filter(course=course).select_related('admin__user')
    
    # Check if student is enrolled
    is_enrolled = False
    if request.user.user_type == 'student':
        student = request.user.student
        is_enrolled = Enrollment.objects.filter(
            student=student, 
            course=course
        ).exists()
    
    context = {
        'course': course,
        'exams': exams,
        'is_enrolled': is_enrolled
    }
    return render(request, 'academics/course_detail.html', context)


@login_required
def create_course(request):
    """Create new course - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can create courses')
        return redirect('course_list')
    
    if request.method == 'POST':
        form = CourseForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Course created successfully')
            return redirect('course_list')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = CourseForm()
    
    return render(request, 'academics/create_course.html', {'form': form})


@login_required
def update_course(request, course_id):
    """Update course - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can update courses')
        return redirect('course_list')
    
    course = get_object_or_404(Course, course_id=course_id)
    
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Course updated successfully')
            return redirect('course_detail', course_id=course_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = CourseForm(instance=course)
    
    context = {'form': form, 'course': course}
    return render(request, 'academics/update_course.html', context)


@login_required
def delete_course(request, course_id):
    """Delete course - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can delete courses')
        return redirect('course_list')
    
    course = get_object_or_404(Course, course_id=course_id)
    
    if request.method == 'POST':
        course_name = course.course_name
        course.delete()
        messages.success(request, f'Course "{course_name}" deleted successfully')
        return redirect('course_list')
    
    context = {'course': course}
    return render(request, 'academics/delete_course.html', context)


@login_required
def bulk_create_courses(request):
    """Bulk create courses - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can create courses')
        return redirect('course_list')
    
    if request.method == 'POST':
        form = BulkCourseCreateForm(request.POST)
        
        if form.is_valid():
            created_courses = form.save()
            messages.success(request, f'Successfully created {len(created_courses)} course(s)')
            return redirect('course_list')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = BulkCourseCreateForm()
    
    return render(request, 'academics/bulk_create_courses.html', {'form': form})