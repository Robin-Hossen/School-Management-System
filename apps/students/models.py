from django.db import models
from apps.accounts.models import CustomUser

# Create your models here.

class Student(models.Model):
    user=models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="student_profile"

    )
    student_id=models.CharField(max_length=20,unique=True)
    date_of_birth=models.DateField(null=True,blank=True)
    gender=models.CharField(max_length=10,blank=True)
    address=models.TextField(blank=True)
    guardian_name=models.CharField(max_length=100,blank=True)
    guardian_email = models.EmailField(blank=True,null=True)
    guardian_phone=models.CharField(max_length=15,blank=True)
    admission_date=models.DateField(auto_now_add=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_id}-{self.user.get_full_name()}"
