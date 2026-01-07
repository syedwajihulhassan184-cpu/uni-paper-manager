from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Prefetch
from django.core.paginator import Paginator
from .models import Enrollment
from .forms import (
    EnrollmentForm, CourseFilterForm, EnrollmentFilterForm,
    BulkEnrollmentForm, StudentSelectionForm, EnrollmentConfirmForm,
    UnenrollmentConfirmForm, BulkUnenrollmentForm, EnrollmentReportForm
)
from academics.models import Course, Program, Department
from accounts.models import Student
from exams.models import Exam, ExamSubmission

# Enrollment Views (Student)

@login_required
def my_enrollments(request):
    """View all enrollments for current student"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related(
        'course__program__department'
    ).annotate(
        exam_count=Count('course__exam')
    ).order_by('-enrollment_date')
    
    context = {'enrollments': enrollments}
    return render(request, 'enrollments/my_enrollments.html', context)


@login_required
def available_courses(request):
    """View courses available for enrollment"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    
    # Get already enrolled courses
    enrolled_course_ids = Enrollment.objects.filter(
        student=student
    ).values_list('course_id', flat=True)
    
    # Get all courses
    courses = Course.objects.select_related(
        'program__department'
    ).annotate(
        exam_count=Count('exam'),
        enrollment_count=Count('enrollment')
    ).exclude(
        course_id__in=enrolled_course_ids
    )
    
    # Apply filters
    filter_form = CourseFilterForm(request.GET)
    if filter_form.is_valid():
        department = filter_form.cleaned_data.get('department')
        program = filter_form.cleaned_data.get('program')
        search_query = filter_form.cleaned_data.get('search_query')
        
        if department:
            courses = courses.filter(program__department=department)
        if program:
            courses = courses.filter(program=program)
        if search_query:
            courses = courses.filter(
                Q(course_name__icontains=search_query) |
                Q(program__program_name__icontains=search_query)
            )
    
    # Pagination
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form
    }
    return render(request, 'enrollments/available_courses.html', context)


@login_required
def enroll_course(request, course_id):
    """Enroll in a course"""
    if request.user.user_type != 'student':
        messages.error(request, 'Only students can enroll in courses')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    course = get_object_or_404(
        Course.objects.select_related('program__department'),
        course_id=course_id
    )
    
    # Check if already enrolled
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course')
        return redirect('course_detail', course_id=course_id)
    
    if request.method == 'POST':
        confirm_form = EnrollmentConfirmForm(request.POST)
        
        if confirm_form.is_valid():
            try:
                Enrollment.objects.create(
                    student=student,
                    course=course
                )
                messages.success(request, f'Successfully enrolled in {course.course_name}')
                return redirect('my_enrollments')
            except Exception as e:
                messages.error(request, f'Enrollment failed: {str(e)}')
        else:
            messages.error(request, 'Please confirm the enrollment')
    else:
        confirm_form = EnrollmentConfirmForm()
    
    context = {
        'course': course,
        'confirm_form': confirm_form
    }
    return render(request, 'enrollments/enroll_course.html', context)


@login_required
def unenroll_course(request, enrollment_id):
    """Unenroll from a course"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('course'),
        enrollment_id=enrollment_id,
        student=student
    )
    
    # Check if student has submitted any exams for this course
    has_submissions = ExamSubmission.objects.filter(
        student=student,
        exam__course=enrollment.course
    ).exists()
    
    if has_submissions:
        messages.error(request, 'Cannot unenroll: You have already submitted exams for this course')
        return redirect('my_enrollments')
    
    if request.method == 'POST':
        form = UnenrollmentConfirmForm(request.POST)
        
        if form.is_valid():
            course_name = enrollment.course.course_name
            enrollment.delete()
            messages.success(request, f'Successfully unenrolled from {course_name}')
            return redirect('my_enrollments')
        else:
            messages.error(request, 'Please confirm the unenrollment')
    else:
        form = UnenrollmentConfirmForm()
    
    context = {
        'enrollment': enrollment,
        'form': form
    }
    return render(request, 'enrollments/unenroll_course.html', context)


@login_required
def enrollment_detail(request, enrollment_id):
    """View details of a specific enrollment"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    enrollment = get_object_or_404(
        Enrollment.objects.select_related(
            'course__program__department'
        ),
        enrollment_id=enrollment_id,
        student=student
    )
    
    # Get exams for this course
    from django.utils import timezone
    now = timezone.now()
    
    exams = Exam.objects.filter(
        course=enrollment.course
    ).annotate(
        is_active=Q(start_time__lte=now, end_time__gte=now),
        is_upcoming=Q(start_time__gt=now),
        is_completed=Q(end_time__lt=now)
    ).order_by('-start_time')
    
    # Get student's submissions for this course
    submissions = ExamSubmission.objects.filter(
        student=student,
        exam__course=enrollment.course
    ).select_related('exam')
    
    submitted_exam_ids = list(submissions.values_list('exam_id', flat=True))
    
    context = {
        'enrollment': enrollment,
        'exams': exams,
        'submitted_exam_ids': submitted_exam_ids,
        'submission_count': submissions.count()
    }
    return render(request, 'enrollments/enrollment_detail.html', context)


# Admin Views for Managing Enrollments

@login_required
def manage_enrollments(request):
    """View and manage all enrollments - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    enrollments = Enrollment.objects.select_related(
        'student__user',
        'student__program',
        'course__program__department'
    ).all()
    
    # Apply filters
    filter_form = EnrollmentFilterForm(request.GET)
    if filter_form.is_valid():
        course = filter_form.cleaned_data.get('course')
        program = filter_form.cleaned_data.get('program')
        search_query = filter_form.cleaned_data.get('search_query')
        
        if course:
            enrollments = enrollments.filter(course=course)
        if program:
            enrollments = enrollments.filter(course__program=program)
        if search_query:
            enrollments = enrollments.filter(
                Q(student__user__full_name__icontains=search_query) |
                Q(student__user__email__icontains=search_query) |
                Q(course__course_name__icontains=search_query)
            )
    
    enrollments = enrollments.order_by('-enrollment_date')
    
    # Pagination
    paginator = Paginator(enrollments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form
    }
    return render(request, 'enrollments/manage_enrollments.html', context)


@login_required
def course_enrollments(request, course_id):
    """View all students enrolled in a specific course - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    course = get_object_or_404(
        Course.objects.select_related('program__department'),
        course_id=course_id
    )
    
    enrollments = Enrollment.objects.filter(
        course=course
    ).select_related(
        'student__user',
        'student__program'
    ).order_by('-enrollment_date')
    
    # Get exam statistics for each student
    exam_count = Exam.objects.filter(course=course).count()
    
    enrollment_data = []
    for enrollment in enrollments:
        submission_count = ExamSubmission.objects.filter(
            student=enrollment.student,
            exam__course=course
        ).count()
        
        enrollment_data.append({
            'enrollment': enrollment,
            'submission_count': submission_count,
            'exam_count': exam_count
        })
    
    context = {
        'course': course,
        'enrollment_data': enrollment_data,
        'total_enrollments': len(enrollment_data)
    }
    return render(request, 'enrollments/course_enrollments.html', context)


@login_required
def student_enrollments_admin(request, student_id):
    """View all enrollments for a specific student - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    student = get_object_or_404(
        Student.objects.select_related('user', 'program__department'),
        student_id=student_id
    )
    
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related(
        'course__program__department'
    ).annotate(
        exam_count=Count('course__exam')
    ).order_by('-enrollment_date')
    
    # Get submission statistics
    enrollment_data = []
    for enrollment in enrollments:
        submission_count = ExamSubmission.objects.filter(
            student=student,
            exam__course=enrollment.course
        ).count()
        
        enrollment_data.append({
            'enrollment': enrollment,
            'submission_count': submission_count
        })
    
    context = {
        'student': student,
        'enrollment_data': enrollment_data,
        'total_enrollments': len(enrollment_data)
    }
    return render(request, 'enrollments/student_enrollments_admin.html', context)


@login_required
def bulk_enroll(request, course_id):
    """Bulk enroll students in a course - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    course = get_object_or_404(Course, course_id=course_id)
    
    if request.method == 'POST':
        form = BulkEnrollmentForm(course=course, data=request.POST)
        
        if form.is_valid():
            enrollments = form.save()
            messages.success(request, f'Successfully enrolled {len(enrollments)} student(s)')
            return redirect('course_enrollments', course_id=course_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = BulkEnrollmentForm(course=course)
    
    context = {
        'course': course,
        'form': form
    }
    return render(request, 'enrollments/bulk_enroll.html', context)


@login_required
def delete_enrollment_admin(request, enrollment_id):
    """Delete an enrollment - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('student__user', 'course'),
        enrollment_id=enrollment_id
    )
    
    if request.method == 'POST':
        student_name = enrollment.student.user.full_name
        course_name = enrollment.course.course_name
        enrollment.delete()
        messages.success(request, f'Removed {student_name} from {course_name}')
        return redirect('manage_enrollments')
    
    context = {'enrollment': enrollment}
    return render(request, 'enrollments/delete_enrollment.html', context)


@login_required
def generate_enrollment_report(request):
    """Generate enrollment report - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        form = EnrollmentReportForm(request.POST)
        
        if form.is_valid():
            report_type = form.cleaned_data.get('report_type')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            format_type = form.cleaned_data.get('format')
            
            # Filter enrollments by date range
            enrollments = Enrollment.objects.all()
            if date_from:
                enrollments = enrollments.filter(enrollment_date__gte=date_from)
            if date_to:
                enrollments = enrollments.filter(enrollment_date__lte=date_to)
            
            # Generate report based on type
            # This is a placeholder - implement actual report generation
            messages.success(request, f'Report generated successfully ({format_type})')
            return redirect('manage_enrollments')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = EnrollmentReportForm()
    
    context = {'form': form}
    return render(request, 'enrollments/generate_report.html', context)