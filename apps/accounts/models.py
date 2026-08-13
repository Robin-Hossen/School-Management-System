from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import CustomUserManager

# Create your models here.

class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    TEACHER = "TEACHER", "Teacher"
    STUDENT = "STUDENT", "Student"
    PARENT = "PARENT", "Parent"
    ACCOUNTANT = "ACCOUNTANT", "Accountant"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)

    phone_number = models.CharField(max_length=15, blank=True)

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    def __str__(self):
        return self.email
