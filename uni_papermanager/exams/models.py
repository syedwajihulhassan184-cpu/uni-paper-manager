from django.db import models
from django.utils import timezone

# Create your models here.

class Exam(models.Model):
    exam_id = models.AutoField(primary_key=True)
    exam_title = models.CharField(max_length=150)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    course = models.ForeignKey('academics.Course', on_delete=models.PROTECT)
    admin = models.ForeignKey('accounts.Admin', on_delete=models.PROTECT)

    def is_active(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
class ExamSubmission(models.Model):
    submission_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('accounts.Student', on_delete=models.PROTECT)
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT)
    submission_time = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to='exam_submissions/')


class Result(models.Model):
    result_id = models.AutoField(primary_key=True)
    submission = models.OneToOneField(ExamSubmission, on_delete=models.CASCADE)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    grade = models.CharField(max_length=2, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)