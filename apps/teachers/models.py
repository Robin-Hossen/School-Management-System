from django.db import models
from django.conf import settings


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )

    teacher_id = models.CharField(
        max_length=20,
        unique=True
    )

    designation = models.CharField(
        max_length=100
    )

    qualification = models.CharField(
        max_length=255,
        blank=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    joining_date = models.DateField()

    address = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.teacher_id} - {self.user.get_full_name()}"