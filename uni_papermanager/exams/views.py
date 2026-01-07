from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q, Prefetch
from django.core.paginator import Paginator
from .models import Exam, ExamSubmission, Result
from .forms import (
    ExamForm, ExamFilterForm, ExamSubmissionForm,
    ResultForm)
from enrollments.models import Enrollment
from accounts.models import Student, Admin

# Exam Views (Admin)

@login_required
def admin_dashboard(request):
    """Admin dashboard with overview"""
    if request.user.user_type != 'admin' or request.user.is_superuser:
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    admin = Admin.objects.get(user=request.user)
    
    # Statistics
    total_exams = Exam.objects.filter(admin=admin).count()
    upcoming_exams = Exam.objects.filter(
        admin=admin,
        start_time__gt=timezone.now()
    ).count()
    active_exams = Exam.objects.filter(
        admin=admin,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).count()
    
    # Recent exams
    recent_exams = Exam.objects.filter(admin=admin).select_related(
        'course__program__department'
    ).order_by('-start_time')[:5]
    
    # Pending submissions (not graded)
    pending_submissions = ExamSubmission.objects.filter(
        exam__admin=admin
    ).exclude(
        submission_id__in=Result.objects.values_list('submission_id', flat=True)
    ).count()
    
    context = {
        'total_exams': total_exams,
        'upcoming_exams': upcoming_exams,
        'active_exams': active_exams,
        'recent_exams': recent_exams,
        'pending_submissions': pending_submissions
    }
    return render(request, 'exams/admin_dashboard.html', context)


@login_required
def create_exam(request):
    """Create new exam - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Only admins can create exams')
        return redirect('student_dashboard')
    
    admin = Admin.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ExamForm(request.POST)
        
        if form.is_valid():
            exam = form.save(commit=False)
            exam.admin = admin
            exam.save()
            messages.success(request, 'Exam created successfully')
            return redirect('exam_list_admin')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ExamForm()
    
    return render(request, 'exams/create_exam.html', {'form': form})


@login_required
def exam_list_admin(request):
    """List all exams created by admin"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    admin = Admin.objects.get(user=request.user)
    
    exams = Exam.objects.filter(admin=admin).select_related(
        'course__program__department'
    ).annotate(
        submission_count=Count('examsubmission')
    )
    
    # Apply filters
    filter_form = ExamFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        course = filter_form.cleaned_data.get('course')
        
        now = timezone.now()
        if status == 'upcoming':
            exams = exams.filter(start_time__gt=now)
        elif status == 'active':
            exams = exams.filter(start_time__lte=now, end_time__gte=now)
        elif status == 'completed':
            exams = exams.filter(end_time__lt=now)
        
        if course:
            exams = exams.filter(course=course)
    
    exams = exams.order_by('-start_time')
    
    # Pagination
    paginator = Paginator(exams, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form
    }
    return render(request, 'exams/exam_list_admin.html', context)


@login_required
def exam_detail_admin(request, exam_id):
    """View exam details with submissions - Admin view"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    admin = Admin.objects.get(user=request.user)
    exam = get_object_or_404(
        Exam.objects.select_related('course__program__department'),
        exam_id=exam_id,
        admin=admin
    )
    
    # Get submissions with student and result info
    submissions = ExamSubmission.objects.filter(exam=exam).select_related(
        'student__user',
        'student__program'
    ).prefetch_related(
        Prefetch('result', queryset=Result.objects.all())
    ).order_by('-submission_time')
    
    # Calculate statistics
    total_submissions = submissions.count()
    graded_count = submissions.filter(
        submission_id__in=Result.objects.values_list('submission_id', flat=True)
    ).count()
    pending_count = total_submissions - graded_count
    
    # Get enrolled students count
    enrolled_students = Enrollment.objects.filter(course=exam.course).count()
    
    context = {
        'exam': exam,
        'submissions': submissions,
        'total_submissions': total_submissions,
        'graded_count': graded_count,
        'pending_count': pending_count,
        'enrolled_students': enrolled_students,
        'is_active': exam.is_active()
    }
    return render(request, 'exams/exam_detail_admin.html', context)


@login_required
def update_exam(request, exam_id):
    """Update exam - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    admin = Admin.objects.get(user=request.user)
    exam = get_object_or_404(Exam, exam_id=exam_id, admin=admin)
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Exam updated successfully')
            return redirect('exam_detail_admin', exam_id=exam_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ExamForm(instance=exam)
    
    context = {'form': form, 'exam': exam}
    return render(request, 'exams/update_exam.html', context)


@login_required
def delete_exam(request, exam_id):
    """Delete exam - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    admin = Admin.objects.get(user=request.user)
    exam = get_object_or_404(Exam, exam_id=exam_id, admin=admin)
    
    if request.method == 'POST':
        exam_title = exam.exam_title
        exam.delete()
        messages.success(request, f'Exam "{exam_title}" deleted successfully')
        return redirect('exam_list_admin')
    
    context = {'exam': exam}
    return render(request, 'exams/delete_exam.html', context)


# Student Exam Views

@login_required
def student_dashboard(request):
    """Student dashboard with available exams"""
    if request.user.user_type != 'student' or request.user.is_superuser:
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    
    # Get enrolled courses
    enrolled_courses = Enrollment.objects.filter(student=student).select_related(
        'course__program__department'
    )
    
    # Get available exams for enrolled courses
    now = timezone.now()
    available_exams = Exam.objects.filter(
        course__in=[e.course for e in enrolled_courses],
        start_time__lte=now,
        end_time__gte=now
    ).select_related('course')
    
    # Upcoming exams
    upcoming_exams = Exam.objects.filter(
        course__in=[e.course for e in enrolled_courses],
        start_time__gt=now
    ).select_related('course').order_by('start_time')[:5]
    
    # Recent submissions
    recent_submissions = ExamSubmission.objects.filter(
        student=student
    ).select_related('exam__course').order_by('-submission_time')[:5]
    
    context = {
        'enrolled_courses': enrolled_courses,
        'available_exams': available_exams,
        'upcoming_exams': upcoming_exams,
        'recent_submissions': recent_submissions
    }
    return render(request, 'exams/student_dashboard.html', context)


@login_required
def exam_list_student(request):
    """List all exams for student's enrolled courses"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    enrolled_courses = Enrollment.objects.filter(student=student).values_list('course_id', flat=True)
    
    exams = Exam.objects.filter(
        course_id__in=enrolled_courses
    ).select_related('course__program__department')
    
    # Apply filters
    filter_form = ExamFilterForm(request.GET)
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        course = filter_form.cleaned_data.get('course')
        
        now = timezone.now()
        if status == 'available':
            exams = exams.filter(start_time__lte=now, end_time__gte=now)
        elif status == 'upcoming':
            exams = exams.filter(start_time__gt=now)
        elif status == 'completed':
            exams = exams.filter(end_time__lt=now)
        
        if course:
            exams = exams.filter(course=course)
    
    exams = exams.order_by('-start_time')
    
    # Get student's submissions
    submitted_exams = ExamSubmission.objects.filter(
        student=student
    ).values_list('exam_id', flat=True)
    
    # Pagination
    paginator = Paginator(exams, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'submitted_exams': list(submitted_exams)
    }
    return render(request, 'exams/exam_list_student.html', context)


@login_required
def exam_detail_student(request, exam_id):
    """View exam details - Student view"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    
    # Check if student is enrolled in the course
    exam = get_object_or_404(
        Exam.objects.select_related('course__program__department'),
        exam_id=exam_id
    )
    
    is_enrolled = Enrollment.objects.filter(
        student=student,
        course=exam.course
    ).exists()
    
    if not is_enrolled:
        messages.error(request, 'You are not enrolled in this course')
        return redirect('exam_list_student')
    
    # Check if already submitted
    submission = ExamSubmission.objects.filter(
        student=student,
        exam=exam
    ).first()
    
    # Get result if exists
    result = None
    if submission:
        try:
            result = Result.objects.get(submission=submission)
        except Result.DoesNotExist:
            pass
    
    context = {
        'exam': exam,
        'is_active': exam.is_active(),
        'submission': submission,
        'result': result
    }
    return render(request, 'exams/exam_detail_student.html', context)


@login_required
def submit_exam(request, exam_id):
    """Submit exam file - Student only"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    exam = get_object_or_404(Exam, exam_id=exam_id)
    
    # Check enrollment
    is_enrolled = Enrollment.objects.filter(
        student=student,
        course=exam.course
    ).exists()
    
    if not is_enrolled:
        messages.error(request, 'You are not enrolled in this course')
        return redirect('exam_list_student')
    
    # Check if exam is active
    if not exam.is_active():
        messages.error(request, 'This exam is not currently active')
        return redirect('exam_detail_student', exam_id=exam_id)
    
    # Check if already submitted
    if ExamSubmission.objects.filter(student=student, exam=exam).exists():
        messages.error(request, 'You have already submitted this exam')
        return redirect('exam_detail_student', exam_id=exam_id)
    
    if request.method == 'POST':
        form = ExamSubmissionForm(request.POST, request.FILES)
        
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = student
            submission.exam = exam
            submission.save()
            messages.success(request, 'Exam submitted successfully!')
            return redirect('exam_detail_student', exam_id=exam_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ExamSubmissionForm()
    
    context = {'form': form, 'exam': exam}
    return render(request, 'exams/submit_exam.html', context)


# Grading Views (Admin)

@login_required
def grade_submission(request, submission_id):
    """Grade a submission - Admin only"""
    if request.user.user_type != 'admin':
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    
    admin = Admin.objects.get(user=request.user)
    submission = get_object_or_404(
        ExamSubmission.objects.select_related(
            'student__user',
            'exam__course'
        ),
        submission_id=submission_id,
        exam__admin=admin
    )
    
    # Check if already graded
    try:
        result = Result.objects.get(submission=submission)
    except Result.DoesNotExist:
        result = None
    
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        
        if form.is_valid():
            result_obj = form.save(commit=False)
            result_obj.submission = submission
            result_obj.save()
            
            if result:
                messages.success(request, 'Grade updated successfully')
            else:
                messages.success(request, 'Submission graded successfully')
            
            return redirect('exam_detail_admin', exam_id=submission.exam.exam_id)
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ResultForm(instance=result)
    
    context = {
        'form': form,
        'submission': submission,
        'result': result
    }
    return render(request, 'exams/grade_submission.html', context)


@login_required
def view_results(request):
    """View all results - Student only"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('admin_dashboard')
    
    student = Student.objects.get(user=request.user)
    
    results = Result.objects.filter(
        submission__student=student
    ).select_related(
        'submission__exam__course'
    ).order_by('-submission__submission_time')
    
    context = {'results': results}
    return render(request, 'exams/view_results.html', context)