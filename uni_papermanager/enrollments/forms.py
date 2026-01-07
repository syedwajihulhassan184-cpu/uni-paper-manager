from django import forms
from django.core.exceptions import ValidationError
from .models import Enrollment
from academics.models import Course, Program, Department
from accounts.models import Student

class EnrollmentForm(forms.ModelForm):
    """Form for enrolling a student in a course"""
    class Meta:
        model = Enrollment
        fields = ['course']
        widgets = {
            'course': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'course': 'Select Course'
        }
    
    def __init__(self, student=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student
        
        # Get courses the student is not already enrolled in
        if student:
            enrolled_course_ids = Enrollment.objects.filter(
                student=student
            ).values_list('course_id', flat=True)
            
            self.fields['course'].queryset = Course.objects.exclude(
                course_id__in=enrolled_course_ids
            ).select_related('program__department').order_by('course_name')
        else:
            self.fields['course'].queryset = Course.objects.select_related(
                'program__department'
            ).all().order_by('course_name')
        
        self.fields['course'].empty_label = 'Select a course to enroll'
        self.fields['course'].label_from_instance = lambda obj: (
            f"{obj.course_name} - {obj.program.program_name} ({obj.program.department.department_name})"
        )
    
    def clean_course(self):
        """Validate enrollment"""
        course = self.cleaned_data.get('course')
        
        if self.student and course:
            # Check if already enrolled
            if Enrollment.objects.filter(student=self.student, course=course).exists():
                raise ValidationError('You are already enrolled in this course')
        
        return course


class CourseFilterForm(forms.Form):
    """Form for filtering available courses"""
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        required=False,
        empty_label='All Programs',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search courses...'
        }),
        label='Search'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all().order_by('department_name')
        self.fields['program'].queryset = Program.objects.select_related('department').all().order_by('program_name')


class EnrollmentFilterForm(forms.Form):
    """Form for filtering enrollments (Admin)"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label='All Courses',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        required=False,
        empty_label='All Programs',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by student name, email, or course...'
        }),
        label='Search'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.select_related('program').all().order_by('course_name')
        self.fields['program'].queryset = Program.objects.all().order_by('program_name')


class BulkEnrollmentForm(forms.Form):
    """Form for bulk enrolling students in a course"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.select_related('program__department').all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        empty_label='Select Course',
        label='Course'
    )
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.select_related('user', 'program').all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Select Students'
    )
    
    def __init__(self, course=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if course:
            # Hide course field and set initial value
            self.fields['course'].initial = course
            self.fields['course'].disabled = True
            
            # Show only students not enrolled in this course
            enrolled_student_ids = Enrollment.objects.filter(
                course=course
            ).values_list('student_id', flat=True)
            
            self.fields['students'].queryset = Student.objects.exclude(
                student_id__in=enrolled_student_ids
            ).select_related('user', 'program').order_by('user__full_name')
        else:
            self.fields['students'].queryset = Student.objects.select_related(
                'user', 'program'
            ).order_by('user__full_name')
        
        # Custom label for students
        self.fields['students'].label_from_instance = lambda obj: (
            f"{obj.user.full_name} ({obj.user.email}) - {obj.program.program_name}"
        )
    
    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        students = cleaned_data.get('students')
        
        if course and students:
            # Check for already enrolled students
            already_enrolled = []
            for student in students:
                if Enrollment.objects.filter(student=student, course=course).exists():
                    already_enrolled.append(student.user.full_name)
            
            if already_enrolled:
                raise ValidationError(
                    f'The following students are already enrolled: {", ".join(already_enrolled)}'
                )
        
        return cleaned_data
    
    def save(self):
        """Create enrollments for all selected students"""
        course = self.cleaned_data['course']
        students = self.cleaned_data['students']
        
        enrollments = []
        for student in students:
            enrollment = Enrollment.objects.create(
                student=student,
                course=course
            )
            enrollments.append(enrollment)
        
        return enrollments


class StudentSelectionForm(forms.Form):
    """Form for selecting students (used in bulk operations)"""
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        required=False,
        empty_label='All Programs',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'filterStudents()'
        }),
        label='Filter by Program'
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search students...',
            'oninput': 'filterStudents()'
        }),
        label='Search'
    )
    student_ids = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Select Students'
    )
    
    def __init__(self, course=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get students not enrolled in the course
        if course:
            enrolled_student_ids = Enrollment.objects.filter(
                course=course
            ).values_list('student_id', flat=True)
            
            available_students = Student.objects.exclude(
                student_id__in=enrolled_student_ids
            ).select_related('user', 'program')
        else:
            available_students = Student.objects.select_related('user', 'program')
        
        # Create choices for student_ids
        choices = [
            (
                student.student_id,
                f"{student.user.full_name} ({student.user.email}) - {student.program.program_name}"
            )
            for student in available_students.order_by('user__full_name')
        ]
        
        self.fields['student_ids'].choices = choices


class EnrollmentConfirmForm(forms.Form):
    """Form for confirming enrollment action"""
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I confirm this enrollment'
    )


class UnenrollmentConfirmForm(forms.Form):
    """Form for confirming unenrollment action"""
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I understand that unenrolling will remove access to all course exams'
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for unenrollment (optional)'
        }),
        label='Reason'
    )


class BulkUnenrollmentForm(forms.Form):
    """Form for bulk unenrolling students"""
    enrollment_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I confirm bulk unenrollment of selected students'
    )
    
    def clean_enrollment_ids(self):
        """Parse enrollment IDs"""
        ids_str = self.cleaned_data.get('enrollment_ids')
        try:
            ids = [int(id) for id in ids_str.split(',') if id.strip()]
            if not ids:
                raise ValidationError('No enrollments selected')
            return ids
        except ValueError:
            raise ValidationError('Invalid enrollment IDs')


class EnrollmentReportForm(forms.Form):
    """Form for generating enrollment reports"""
    report_type = forms.ChoiceField(
        choices=[
            ('by_course', 'By Course'),
            ('by_program', 'By Program'),
            ('by_department', 'By Department'),
            ('by_student', 'By Student'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Report Type'
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='From Date'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='To Date'
    )
    format = forms.ChoiceField(
        choices=[
            ('html', 'HTML'),
            ('csv', 'CSV'),
            ('pdf', 'PDF'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Export Format'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('End date must be after start date')
        
        return cleaned_data