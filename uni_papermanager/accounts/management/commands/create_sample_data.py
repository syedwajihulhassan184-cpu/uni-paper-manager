from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, Student, Admin
from academics.models import Department, Program, Course
from exams.models import Exam
from enrollments.models import Enrollment
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Creates sample data for testing'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating sample data...')
        
        with transaction.atomic():
            # Create Departments
            cs_dept = Department.objects.create(department_name='Computer Science')
            math_dept = Department.objects.create(department_name='Mathematics')
            eng_dept = Department.objects.create(department_name='Engineering')
            
            self.stdout.write(self.style.SUCCESS('✓ Created 3 departments'))
            
            # Create Programs
            bscs = Program.objects.create(
                program_name='BS Computer Science',
                department=cs_dept
            )
            mscs = Program.objects.create(
                program_name='MS Computer Science',
                department=cs_dept
            )
            bsmath = Program.objects.create(
                program_name='BS Mathematics',
                department=math_dept
            )
            
            self.stdout.write(self.style.SUCCESS('✓ Created 3 programs'))
            
            # Create Courses
            courses = [
                Course.objects.create(course_name='Data Structures', program=bscs),
                Course.objects.create(course_name='Algorithms', program=bscs),
                Course.objects.create(course_name='Database Systems', program=bscs),
                Course.objects.create(course_name='Web Development', program=bscs),
                Course.objects.create(course_name='Machine Learning', program=mscs),
                Course.objects.create(course_name='Calculus I', program=bsmath),
            ]
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(courses)} courses'))
            
            # Create Admin
            admin_user = User.objects.create_user(
                email='admin@test.com',
                password='admin123',
                full_name='John Admin',
                user_type='admin'
            )
            admin = Admin.objects.create(user=admin_user)
            
            self.stdout.write(self.style.SUCCESS('✓ Created admin user (admin@test.com / admin123)'))
            
            # Create Students
            students = []
            for i in range(1, 11):
                user = User.objects.create_user(
                    email=f'student{i}@test.com',
                    password='student123',
                    full_name=f'Student {i}',
                    user_type='student'
                )
                student = Student.objects.create(user=user, program=bscs)
                students.append(student)
            
            self.stdout.write(self.style.SUCCESS('✓ Created 10 students (student1-10@test.com / student123)'))
            
            # Enroll students in courses
            for student in students[:5]:
                for course in courses[:3]:
                    Enrollment.objects.create(student=student, course=course)
            
            self.stdout.write(self.style.SUCCESS('✓ Created enrollments'))
            
            # Create Exams
            now = timezone.now()
            exams = [
                Exam.objects.create(
                    exam_title='Midterm Exam - Data Structures',
                    start_time=now + timedelta(days=1),
                    end_time=now + timedelta(days=1, hours=2),
                    course=courses[0],
                    admin=admin
                ),
                Exam.objects.create(
                    exam_title='Final Exam - Algorithms',
                    start_time=now + timedelta(days=7),
                    end_time=now + timedelta(days=7, hours=3),
                    course=courses[1],
                    admin=admin
                ),
                Exam.objects.create(
                    exam_title='Quiz 1 - Database Systems',
                    start_time=now + timedelta(hours=1),
                    end_time=now + timedelta(hours=2),
                    course=courses[2],
                    admin=admin
                ),
            ]
            
            self.stdout.write(self.style.SUCCESS(f'✓ Created {len(exams)} exams'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Sample Data Created Successfully ==='))
        self.stdout.write('\nLogin Credentials:')
        self.stdout.write('Admin: admin@test.com / admin123')
        self.stdout.write('Students: student1@test.com / student123 (up to student10@test.com)')