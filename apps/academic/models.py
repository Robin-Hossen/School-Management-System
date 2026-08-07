from django.db import models

# Create your models here.

class AcademicSession(models.Model):
    name=models.CharField(max_length=20,unique=True)
    start_date=models.DateField()
    end_date=models.DateField()

    is_active=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#create a Class
class Class(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10)

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="classes"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "section", "academic_session")

    def __str__(self):
        return f"{self.name} - {self.section}"   


#subject model
# 
class Subject(models.Model):
    name=models.CharField(max_length=100)
    code=models.CharField(max_length=20,unique=True)
    class_name=models.ForeignKey(
        "academic.Class", #Class model is in the same app, so we can use "academic.Class" to refer to it
        on_delete=models.CASCADE,
        related_name="subjects"
    )   
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.code}"      


#section model

class Section(models.Model):
    name = models.CharField(max_length=10)

    class_name = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="sections"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "class_name")

    def __str__(self):
        return f"{self.class_name} - {self.name}"

#Enrollment model
# 
class Enrollment(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        COMPLETED = "COMPLETED", "Completed"

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    class_name = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="enrollments"
    )

    enrollment_date = models.DateField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "student",
            "academic_session",
        )

    def __str__(self):
        return f"{self.student} - {self.academic_session}"    


#TeacherAssignment model
class TeachingAssignment(models.Model):
    teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    class_name = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="teaching_assignments"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "teacher",
                    "subject",
                    "class_name",
                    "section",
                    "academic_session",
                ],
                name="unique_teaching_assignment"
            )
        ]

    def __str__(self):
        return (
            f"{self.teacher.teacher_id} - "
            f"{self.subject.name} - "
            f"{self.class_name.name} - "
            f"{self.section.name}"
        )   