from django.db import models

# Create your models here.

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name

class Program(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return self.program_name

    class META:
        indexes = [models.Index(fields=['department'])]

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100)
    program = models.ForeignKey(Program, on_delete=models.PROTECT)

    def __str__(self):
        return self.course_name

    class METAL:
        indexes = [models.Index(fields=['program'])]