from django.db import models

# Create your models here.

class Enrollment(models.Model):
    enrollment_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('accounts.Student', on_delete=models.PROTECT)
    course = models.ForeignKey('academics.Course', on_delete=models.PROTECT)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'course')
