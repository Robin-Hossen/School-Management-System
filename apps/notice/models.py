from django.db import models


class Notice(models.Model):

    AUDIENCE_CHOICES = [
        ("ALL", "All"),
        ("STUDENT", "Student"),
        ("TEACHER", "Teacher"),
        ("STAFF", "Staff"),
    ]

    title = models.CharField(max_length=200)

    content = models.TextField()

    publish_date = models.DateField()

    target_audience = models.CharField(
        max_length=20,
        choices=AUDIENCE_CHOICES,
        default="ALL"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title