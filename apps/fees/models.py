from django.db import models
from apps.academic.models import AcademicSession, Class
from apps.students.models import Student


class FeeStructure(models.Model):
    name = models.CharField(max_length=100)

    academic_session = models.ForeignKey(
        AcademicSession,
        on_delete=models.CASCADE,
        related_name="fee_structures"
    )

    class_name = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="fee_structures"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    due_date = models.DateField()

    description = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.name} - {self.class_name.name}"






class StudentFee(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="fees"
    )

    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.CASCADE,
        related_name="student_fees"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    due_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ("PENDING", "Pending"),
            ("PARTIAL", "Partial"),
            ("PAID", "Paid"),
        ],
        default="PENDING"
    )

    due_date = models.DateField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "fee_structure"],
                name="unique_student_fee"
            )
        ]

    def __str__(self):
        return f"{self.student.student_id} - {self.fee_structure.name}"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("CASH", "Cash"),
        ("BANK", "Bank"),
        ("MOBILE_BANKING", "Mobile Banking"),
        ("CARD", "Card"),
        ("ONLINE","Online"),
    ]

    student_fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    payment_date = models.DateField()

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    transaction_id = models.CharField(
        max_length=100,
        blank=True
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True
    )

    stripe_payment_intent_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    remarks = models.CharField(
        max_length=255,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.student_fee.student.student_id} - {self.amount}"    