from django.db import models
from apps.academic.models import AcademicSession, Class, Subject


class Exam(models.Model):
    name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=50)
    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="exams"
    )
    class_name = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="exams"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.exam_type} - {self.academic_session.name} - {self.class_name.name}"

class ExamSubject(models.Model):
    
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="exam_subjects"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="exam_subjects"
    )

    exam_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_marks = models.PositiveIntegerField(default=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["exam", "subject"],
                name="unique_exam_subject"
            )
        ]


class Result(models.Model):
   
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="results"
    )

    exam_subject = models.ForeignKey(
        ExamSubject,
        on_delete=models.CASCADE,
        related_name="results"
    )

    marks_obtained = models.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    grade = models.CharField(
        max_length=5,
        blank=True
    )

    remarks = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "exam_subject"],
                name="unique_student_exam_subject_result"
            )
        ]       