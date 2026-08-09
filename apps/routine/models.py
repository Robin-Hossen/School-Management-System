from django.db import models
from apps.academic.models import TeachingAssignment


class Routine(models.Model):

    class DayOfWeek(models.TextChoices):
        SATURDAY = "SATURDAY", "Saturday"
        SUNDAY = "SUNDAY", "Sunday"
        MONDAY = "MONDAY", "Monday"
        TUESDAY = "TUESDAY", "Tuesday"
        WEDNESDAY = "WEDNESDAY", "Wednesday"
        THURSDAY = "THURSDAY", "Thursday"

    teaching_assignment = models.ForeignKey(
        TeachingAssignment,
        on_delete=models.CASCADE,
        related_name="routines"
    )

    day = models.CharField(
        max_length=15,
        choices=DayOfWeek.choices
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    room_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "teaching_assignment",
                    "day",
                    "start_time",
                    "end_time",
                ],
                name="unique_routine_schedule"
            )
        ]

    def __str__(self):
        return f"{self.teaching_assignment} - {self.day}"