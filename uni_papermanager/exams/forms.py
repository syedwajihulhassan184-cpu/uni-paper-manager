from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Exam, ExamSubmission, Result
from academics.models import Course
import os

class ExamForm(forms.ModelForm):
    """Form for creating and updating exams"""
    class Meta:
        model = Exam
        fields = ['exam_title', 'start_time', 'end_time', 'course']
        widgets = {
            'exam_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter exam title',
                'maxlength': 150
            }),
            'start_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_time': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'course': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'exam_title': 'Exam Title',
            'start_time': 'Start Time',
            'end_time': 'End Time',
            'course': 'Course'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show course with program and department info
        self.fields['course'].queryset = Course.objects.select_related(
            'program__department'
        ).all().order_by('course_name')
        self.fields['course'].empty_label = 'Select Course'
        self.fields['course'].label_from_instance = lambda obj: (
            f"{obj.course_name} - {obj.program.program_name} ({obj.program.department.department_name})"
        )
    
    def clean(self):
        """Validate exam timing"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            # Check if end time is after start time
            if end_time <= start_time:
                raise ValidationError('End time must be after start time')
            
            # Check if start time is in the past (only for new exams)
            if not self.instance.pk:  # New exam
                if start_time < timezone.now():
                    raise ValidationError('Start time cannot be in the past')
            
            # Check if exam duration is reasonable (at least 15 minutes)
            duration = end_time - start_time
            if duration.total_seconds() < 900:  # 15 minutes
                raise ValidationError('Exam duration must be at least 15 minutes')
            
            # Check if exam duration is not too long (max 24 hours)
            if duration.total_seconds() > 86400:  # 24 hours
                raise ValidationError('Exam duration cannot exceed 24 hours')
        
        return cleaned_data


class ExamFilterForm(forms.Form):
    """Form for filtering exams"""
    STATUS_CHOICES = [
        ('all', 'All Exams'),
        ('upcoming', 'Upcoming'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.select_related('program__department').all(),
        required=False,
        empty_label='All Courses',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course'].queryset = Course.objects.select_related(
            'program__department'
        ).all().order_by('course_name')


class ExamSubmissionForm(forms.ModelForm):
    """Form for submitting exam files"""
    class Meta:
        model = ExamSubmission
        fields = ['file_path']
        widgets = {
            'file_path': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.zip'
            })
        }
        labels = {
            'file_path': 'Upload Exam File'
        }
        help_texts = {
            'file_path': 'Accepted formats: PDF, DOC, DOCX, TXT, ZIP (Max size: 10MB)'
        }
    
    def clean_file_path(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file_path')
        
        if file:
            # Check file size (max 10MB)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('File size cannot exceed 10MB')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.zip']
            ext = os.path.splitext(file.name)[1].lower()
            
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
                )
        
        return file


class ResultForm(forms.ModelForm):
    """Form for grading exam submissions"""
    class Meta:
        model = Result
        fields = ['marks', 'grade', 'feedback']
        widgets = {
            'marks': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter marks',
                'min': 0,
                'max': 100,
                'step': 0.01
            }),
            'grade': forms.Select(attrs={
                'class': 'form-control'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter feedback for the student'
            })
        }
        labels = {
            'marks': 'Marks (out of 100)',
            'grade': 'Grade',
            'feedback': 'Feedback'
        }
    
    GRADE_CHOICES = [
        ('', 'Select Grade'),
        ('A+', 'A+ (90-100)'),
        ('A', 'A (85-89)'),
        ('A-', 'A- (80-84)'),
        ('B+', 'B+ (75-79)'),
        ('B', 'B (70-74)'),
        ('B-', 'B- (65-69)'),
        ('C+', 'C+ (60-64)'),
        ('C', 'C (55-59)'),
        ('C-', 'C- (50-54)'),
        ('D', 'D (40-49)'),
        ('F', 'F (0-39)'),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].choices = self.GRADE_CHOICES
        self.fields['grade'].required = False
        self.fields['feedback'].required = False
    
    def clean_marks(self):
        """Validate marks are within valid range"""
        marks = self.cleaned_data.get('marks')
        
        if marks is not None:
            if marks < 0:
                raise ValidationError('Marks cannot be negative')
            if marks > 100:
                raise ValidationError('Marks cannot exceed 100')
        
        return marks
    
    def clean(self):
        """Auto-assign grade based on marks if not provided"""
        cleaned_data = super().clean()
        marks = cleaned_data.get('marks')
        grade = cleaned_data.get('grade')
        
        # Auto-assign grade if not provided
        if marks is not None and not grade:
            if marks >= 90:
                cleaned_data['grade'] = 'A+'
            elif marks >= 85:
                cleaned_data['grade'] = 'A'
            elif marks >= 80:
                cleaned_data['grade'] = 'A-'
            elif marks >= 75:
                cleaned_data['grade'] = 'B+'
            elif marks >= 70:
                cleaned_data['grade'] = 'B'
            elif marks >= 65:
                cleaned_data['grade'] = 'B-'
            elif marks >= 60:
                cleaned_data['grade'] = 'C+'
            elif marks >= 55:
                cleaned_data['grade'] = 'C'
            elif marks >= 50:
                cleaned_data['grade'] = 'C-'
            elif marks >= 40:
                cleaned_data['grade'] = 'D'
            else:
                cleaned_data['grade'] = 'F'
        
        return cleaned_data


class BulkGradeForm(forms.Form):
    """Form for bulk grading multiple submissions"""
    default_marks = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Default marks for all',
            'min': 0,
            'max': 100
        }),
        label='Default Marks'
    )
    default_grade = forms.ChoiceField(
        choices=[('', 'Select Grade')] + ResultForm.GRADE_CHOICES[1:],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Default Grade'
    )
    default_feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Default feedback for all submissions'
        }),
        label='Default Feedback'
    )
    submission_ids = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    def clean_submission_ids(self):
        """Parse submission IDs"""
        ids_str = self.cleaned_data.get('submission_ids')
        try:
            ids = [int(id) for id in ids_str.split(',') if id.strip()]
            return ids
        except ValueError:
            raise ValidationError('Invalid submission IDs')


class ExamSearchForm(forms.Form):
    """Form for searching exams"""
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by exam title or course name...'
        }),
        label='Search'
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
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to:
            if date_to < date_from:
                raise ValidationError('End date must be after start date')
        
        return cleaned_data