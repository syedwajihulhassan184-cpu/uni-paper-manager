from django import forms
from django.core.exceptions import ValidationError
from .models import Department, Program, Course

class DepartmentForm(forms.ModelForm):
    """Form for creating and updating departments"""
    class Meta:
        model = Department
        fields = ['department_name']
        widgets = {
            'department_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department name',
                'maxlength': 100
            })
        }
        labels = {
            'department_name': 'Department Name'
        }
    
    def clean_department_name(self):
        """Validate department name is unique"""
        department_name = self.cleaned_data.get('department_name')
        
        # Check for duplicate (excluding current instance if updating)
        queryset = Department.objects.filter(department_name__iexact=department_name)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('A department with this name already exists')
        
        return department_name


class ProgramForm(forms.ModelForm):
    """Form for creating and updating programs"""
    class Meta:
        model = Program
        fields = ['program_name', 'department']
        widgets = {
            'program_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter program name',
                'maxlength': 100
            }),
            'department': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'program_name': 'Program Name',
            'department': 'Department'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize department choices display
        self.fields['department'].queryset = Department.objects.all().order_by('department_name')
        self.fields['department'].empty_label = 'Select Department'
    
    def clean(self):
        """Validate program name is unique within department"""
        cleaned_data = super().clean()
        program_name = cleaned_data.get('program_name')
        department = cleaned_data.get('department')
        
        if program_name and department:
            # Check for duplicate within same department
            queryset = Program.objects.filter(
                program_name__iexact=program_name,
                department=department
            )
            
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError(
                    f'A program with name "{program_name}" already exists in {department.department_name}'
                )
        
        return cleaned_data


class CourseForm(forms.ModelForm):
    """Form for creating and updating courses"""
    class Meta:
        model = Course
        fields = ['course_name', 'program']
        widgets = {
            'course_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course name',
                'maxlength': 100
            }),
            'program': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'course_name': 'Course Name',
            'program': 'Program'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show program with department info
        self.fields['program'].queryset = Program.objects.select_related('department').all().order_by('program_name')
        self.fields['program'].empty_label = 'Select Program'
        
        # Custom label for program to show department
        self.fields['program'].label_from_instance = lambda obj: f"{obj.program_name} ({obj.department.department_name})"
    
    def clean(self):
        """Validate course name is unique within program"""
        cleaned_data = super().clean()
        course_name = cleaned_data.get('course_name')
        program = cleaned_data.get('program')
        
        if course_name and program:
            # Check for duplicate within same program
            queryset = Course.objects.filter(
                course_name__iexact=course_name,
                program=program
            )
            
            if self.instance and self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise ValidationError(
                    f'A course with name "{course_name}" already exists in {program.program_name}'
                )
        
        return cleaned_data


class CourseFilterForm(forms.Form):
    """Form for filtering courses"""
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Order by name
        self.fields['department'].queryset = Department.objects.all().order_by('department_name')
        self.fields['program'].queryset = Program.objects.select_related('department').all().order_by('program_name')


class ProgramFilterForm(forms.Form):
    """Form for filtering programs"""
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'onchange': 'this.form.submit()'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all().order_by('department_name')


class BulkCourseCreateForm(forms.Form):
    """Form for creating multiple courses at once"""
    program = forms.ModelChoiceField(
        queryset=Program.objects.select_related('department').all(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Program',
        empty_label='Select Program'
    )
    course_names = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Enter course names (one per line)\nExample:\nIntroduction to Programming\nData Structures\nWeb Development'
        }),
        label='Course Names',
        help_text='Enter one course name per line'
    )
    
    def clean_course_names(self):
        """Parse and validate course names"""
        course_names_text = self.cleaned_data.get('course_names')
        
        # Split by newlines and remove empty lines
        course_names = [name.strip() for name in course_names_text.split('\n') if name.strip()]
        
        if not course_names:
            raise ValidationError('Please enter at least one course name')
        
        # Check for duplicates in input
        if len(course_names) != len(set(course_names)):
            raise ValidationError('Duplicate course names found in input')
        
        return course_names
    
    def save(self):
        """Create all courses"""
        program = self.cleaned_data['program']
        course_names = self.cleaned_data['course_names']
        
        created_courses = []
        for course_name in course_names:
            # Check if course already exists
            if not Course.objects.filter(course_name=course_name, program=program).exists():
                course = Course.objects.create(
                    course_name=course_name,
                    program=program
                )
                created_courses.append(course)
        
        return created_courses