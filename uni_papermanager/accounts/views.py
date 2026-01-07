from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import User, Student, Admin
from .forms import (
    LoginForm, StudentRegistrationForm, AdminRegistrationForm,
    ProfileUpdateForm, ChangePasswordForm, StudentProgramUpdateForm
)

# Authentication Views

def login_view(request):
    """Handle user login for both students and admins"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('username')  # username field contains email
            password = form.cleaned_data.get('password')
            
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.full_name}!')
                
                # Redirect based on user type
                if user.user_type == 'student':
                    return redirect('student_dashboard')
                elif user.user_type == 'admin':
                    return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def register_student(request):
    """Student registration"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Registration successful! Please login.')
                return redirect('login')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/register_student.html', {'form': form})


def register_admin(request):
    """Admin registration - can be restricted to superuser only"""
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can create admin accounts')
        return redirect('login')
    
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Admin account created successfully')
                return redirect('admin_dashboard')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'accounts/register_admin.html', {'form': form})


@login_required
def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    if request.user.user_type == 'student':
        return redirect('student_dashboard')
    elif request.user.user_type == 'admin' or request.user.is_superuser:
        return redirect('admin_dashboard')
    return redirect('login')


@login_required
def profile_view(request):
    """View and edit user profile"""
    if request.user.user_type == 'student':
        student = Student.objects.select_related('user', 'program__department').get(user=request.user)
        program_form = None
        
        context = {
            'student': student,
            'user_type': 'student',
            'program_form': program_form
        }
    else:
        admin = Admin.objects.select_related('user').get(user=request.user)
        context = {
            'admin': admin,
            'user_type': 'admin'
        }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def update_profile(request):
    """Update user profile information"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'accounts/update_profile.html', {'form': form})


@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = ChangePasswordForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully. Please login again.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = ChangePasswordForm(user=request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def update_student_program(request):
    """Update student's program - Student only"""
    if request.user.user_type != 'student':
        messages.error(request, 'Access denied')
        return redirect('profile')
    
    student = Student.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = StudentProgramUpdateForm(request.POST, instance=student)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Program updated successfully')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below')
    else:
        form = StudentProgramUpdateForm(instance=student)
    
    return render(request, 'accounts/update_program.html', {'form': form})


def access_denied(request):
    """Access denied page"""
    return render(request, 'accounts/access_denied.html', status=403)