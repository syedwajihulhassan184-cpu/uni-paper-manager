# 🎓 University Papers Manager - Online Exam Management System

A Django-based web application for managing online examinations, student enrollments, and academic courses with role-based access control.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![SQL Server](https://img.shields.io/badge/SQL%20Server-2019-red)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## ✨ Features

### 🔐 User Management
- **Dual Role System**: Students and Administrators
- **Secure Authentication**: Email-based login with password hashing
- **Profile Management**: Update personal information and change passwords
- **Role-Based Access Control**: Automatic routing based on user type

### 📚 Academic Structure
- **Hierarchical Organization**: Department → Program → Course
- **Department Management**: Create and manage academic departments
- **Program Management**: Define degree programs within departments
- **Course Management**: Create courses with program associations
- **Bulk Operations**: Create multiple courses at once

### 📝 Examination System
- **Timed Exams**: Set start and end times with automatic availability
- **File Submission**: Students upload exam files (PDF, DOC, DOCX, TXT, ZIP)
- **File Validation**: Size limit (10MB) and format checking
- **Multiple Submissions**: Track submission history per student
- **Exam Status Tracking**: Active, Upcoming, and Completed states

### 👨‍🎓 Student Features
- Browse and enroll in courses across departments
- View dashboard with active and upcoming exams
- Submit exam files during active periods
- Download submitted files for reference
- View grades and instructor feedback
- Track academic progress with visual indicators

### 👨‍🏫 Admin Features
- Create and manage exams with timing controls
- View all student submissions with details
- Download student submission files
- Grade submissions with marks (0-100)
- Auto-grade calculation (A+ to F scale)
- Add detailed feedback for students
- Bulk enrollment operations
- Comprehensive statistics dashboard

### 🎨 User Interface
- **Modern Design**: Clean Bootstrap 5 interface
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Dashboard**: Real-time statistics and metrics
- **Progress Indicators**: Visual representation of grades
- **Status Badges**: Clear indication of exam and submission states
- **Toast Notifications**: Auto-dismissing success/error messages

### 🔒 Security Features
- CSRF protection on all forms
- XSS prevention through template escaping
- SQL injection protection via Django ORM
- Password strength validation
- File upload security checks
- Role-based middleware protection
- Session management and timeout

---

## 🚀 Quick Start

### Prerequisites

```bash
- Python 3.11 or higher
- SQL Server 2019+ or SQL Server Express
- ODBC Driver 17 for SQL Server
- pip (Python package manager)
- Virtual environment tool
```

### Installation Steps

1. **Clone the repository**
```bash
cd "E:\UNI PAPERS MANAGER"
```

2. **Create and activate virtual environment**
```bash
python -m venv env
env\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a `.env` file in the project root:
```env
DB_NAME=OnlineExamDB
DB_USER=sa
DB_PASSWORD=YourPassword
DB_HOST=localhost
DB_PORT=1433

SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. **Create database**
```sql
-- In SQL Server Management Studio or sqlcmd
CREATE DATABASE OnlineExamDB;
```

6. **Run migrations**
```bash
cd uni_papermanager
python manage.py makemigrations
python manage.py migrate
```

7. **Create sample data (optional)**
```bash
python manage.py create_sample_data
```

8. **Run the development server**
```bash
python manage.py runserver
```

9. **Access the application**
```
Main Application: http://localhost:8000/
Admin Panel: http://localhost:8000/admin/
```

---

## 🔑 Default Credentials

### Admin Account
```
Email: admin@test.com
Password: admin123
```

### Student Accounts
```
Email: student1@test.com to student10@test.com
Password: student123
```

**Note**: First 5 students (student1-5) are pre-enrolled in sample courses.

---

## 📁 Project Structure

```
uni_papermanager/
├── accounts/                   # User authentication & management
│   ├── forms.py               # Login, Registration, Profile forms
│   ├── views.py               # Authentication views
│   ├── models.py              # User, Student, Admin models
│   ├── middleware.py          # Role-based access control
│   ├── templates/             # Account templates
│   └── management/
│       └── commands/
│           └── create_sample_data.py
├── academics/                  # Academic structure management
│   ├── forms.py               # Department, Program, Course forms
│   ├── views.py               # CRUD views for academics
│   ├── models.py              # Academic models
│   └── templates/             # Academic templates
├── exams/                      # Exam & grading management
│   ├── forms.py               # Exam, Submission, Grading forms
│   ├── views.py               # Exam and grading views
│   ├── models.py              # Exam, Submission, Result models
│   ├── middleware.py          # Exam timing & access control
│   └── templates/             # Exam templates
├── enrollments/                # Course enrollment management
│   ├── forms.py               # Enrollment forms
│   ├── views.py               # Enrollment views
│   ├── models.py              # Enrollment model
│   └── templates/             # Enrollment templates
├── static/
│   ├── css/                   # Custom stylesheets
│   ├── js/
│   │   └── form-validation.js # Client-side validation
│   └── images/
├── media/
│   └── exam_submissions/      # Uploaded exam files
├── templates/
│   └── base.html              # Base template
├── manage.py
├── requirements.txt
└── README.md
```

---

## 💻 Technology Stack

### Backend
- **Framework**: Django 4.2.8
- **Database**: Microsoft SQL Server 2019+
- **Database Driver**: mssql-django, pyodbc
- **Image Processing**: Pillow
- **Configuration**: python-decouple

### Frontend
- **CSS Framework**: Bootstrap 5.3
- **Icons**: Font Awesome 6.4
- **JavaScript**: Vanilla JS with client-side validation
- **Template Engine**: Django Templates

### Middleware & Security
- CSRF Protection
- Role-Based Access Control
- Exam Timing Validation
- Activity Logging
- Security Headers

---

## 📊 Database Schema

### Core Tables
- **Department** - Academic departments
- **Program** - Degree programs
- **Course** - Individual courses
- **User** - Base user authentication
- **Student** - Student profiles linked to programs
- **Admin** - Administrator profiles
- **Exam** - Exam definitions with timing
- **Enrollment** - Student-course relationships
- **ExamSubmission** - Uploaded exam files
- **Result** - Grades and feedback

### Key Relationships
```
Department (1) → (Many) Program
Program (1) → (Many) Course
Program (1) → (Many) Student
Course (1) → (Many) Exam
Student (Many) ← (Many) Course (via Enrollment)
Exam (1) → (Many) ExamSubmission
ExamSubmission (1) → (1) Result
Admin (1) → (Many) Exam
```

---

## 🎯 Usage Guide

### For Students

1. **Register/Login**
   - Navigate to http://localhost:8000/register/student/
   - Fill in details and select your program
   - Login with credentials

2. **Enroll in Courses**
   - Browse available courses
   - Filter by department/program
   - Click "Enroll Now"

3. **Take Exams**
   - View active exams on dashboard
   - Click exam to view details
   - Upload exam file during active period
   - Download submission for records

4. **View Results**
   - Navigate to "My Results"
   - View grades and feedback
   - Track performance over time

### For Admins

1. **Set Up Academic Structure**
   - Create Departments
   - Add Programs to departments
   - Create Courses in programs

2. **Create Exams**
   - Select course
   - Set exam title
   - Define start/end times
   - Save exam

3. **Manage Submissions**
   - View exam details
   - Download student files
   - Review submissions

4. **Grade Students**
   - Click "Grade" on submission
   - Enter marks (0-100)
   - Grade auto-calculated or manual
   - Add feedback
   - Save results

---


## 📋 Management Commands

### Create Sample Data
```bash
python manage.py create_sample_data
```
Creates:
- 3 Departments
- 3 Programs
- 6 Courses
- 1 Admin account
- 10 Student accounts
- Sample enrollments
- 3 Sample exams

### Export Users
```bash
python manage.py export_users --type=student --output=students.csv
```

### Generate Statistics Report
```bash
python manage.py generate_report
```

### Clean Old Submissions
```bash
python manage.py cleanup_old_submissions --days=365
```

---

## 🔧 Configuration

### Database Settings
Edit `settings.py` or use `.env` file:
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'OnlineExamDB',
        'USER': 'sa',
        'PASSWORD': 'YourPassword',
        'HOST': 'localhost',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}
```

### File Upload Settings
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Max upload size (handled in form validation)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
```

### Allowed File Formats
Modify in `exams/forms.py`:
```python
allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.zip']
```

---

## 🎨 Customization

### Change Theme Colors
Edit `templates/base.html` CSS variables:
```css
:root {
    --primary-color: #4F46E5;
    --secondary-color: #10B981;
    --danger-color: #EF4444;
    --warning-color: #F59E0B;
}
```

### Modify Grade Scale
Edit `exams/forms.py` in `ResultForm`:
```python
def clean(self):
    # Modify grade thresholds here
    if marks >= 90:
        cleaned_data['grade'] = 'A+'
    # ... etc
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue: Database connection failed**
```
Solution: 
1. Verify SQL Server is running
2. Check credentials in .env file
3. Test connection: sqlcmd -S localhost -U sa -P YourPassword
```

**Issue: Templates not found**
```
Solution:
1. Ensure templates directory exists
2. Check TEMPLATES setting in settings.py
3. Verify app is in INSTALLED_APPS
```

**Issue: Static files not loading**
```
Solution:
1. Run: python manage.py collectstatic
2. Check DEBUG=True for development
3. Verify STATIC_ROOT and STATIC_URL settings
```

**Issue: File upload fails**
```
Solution:
1. Check MEDIA_ROOT permissions
2. Verify max upload size
3. Check disk space
4. Ensure file format is allowed
```


## 📝 Features Summary

| Feature | Status |
|---------|--------|
| User Authentication | ✅ Complete |
| Role-Based Access | ✅ Complete |
| Department Management | ✅ Complete |
| Program Management | ✅ Complete |
| Course Management | ✅ Complete |
| Exam Creation | ✅ Complete |
| File Upload | ✅ Complete |
| Exam Submission | ✅ Complete |
| Grading System | ✅ Complete |
| Result Viewing | ✅ Complete |
| Enrollment System | ✅ Complete |
| Bulk Operations | ✅ Complete |
| Search & Filter | ✅ Complete |
| Responsive Design | ✅ Complete |
| Form Validation | ✅ Complete |
| Security Features | ✅ Complete |

---

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Check existing documentation
- Review error logs in `logs/` directory



## 👥 Credits

Developed as a comprehensive university papers and exam management solution.

### Technologies Used
- Django Framework
- Bootstrap 5
- Font Awesome
- Microsoft SQL Server


## 📊 Project Statistics

- **Lines of Code**: 5,000+
- **Forms**: 27
- **Views**: 52
- **Templates**: 30+
- **Models**: 9
- **Middleware**: 7

---

## 🎓 Academic Use

This system is designed for educational institutions to:
- Manage multiple departments and programs
- Conduct online examinations
- Track student performance
- Maintain academic records
- Facilitate remote learning

---

**Made with ❤️ for Education**

Last Updated: January 2026  
Version: 1.0.0  
Status: Production Ready ✅

---

## Quick Links

- 🏠 [Home](http://localhost:8000/)
- 📝 [Login](http://localhost:8000/login/)
- 📚 [Courses](http://localhost:8000/academics/courses/)
- 📋 [Exams](http://localhost:8000/exams/)
- 👤 [Profile](http://localhost:8000/profile/)

---

**Need Help?** Check the troubleshooting section or create an issue!
