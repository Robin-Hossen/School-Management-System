from django_filters.rest_framework import DjangoFilterBackend
from .services.email_service import send_payment_confirmation
from django.core.mail import send_mail
from django.conf import settings

from decimal import Decimal
from rest_framework import status
from rest_framework.response import Response

from rest_framework import filters, viewsets

from apps.accounts.models import UserRole


from apps.accounts.permissions import (
    FeeStructurePermission,
    StudentFeePermission,
    PaymentPermission,
)

from .filters import (
    FeeStructureFilter,
    StudentFeeFilter,
    PaymentFilter,
)

from .models import FeeStructure, StudentFee, Payment

from .serializers import (
    FeeStructureSerializer,
    StudentFeeSerializer,
    PaymentSerializer,
)


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.all()
    serializer_class = FeeStructureSerializer
    permission_classes = [FeeStructurePermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = FeeStructureFilter

    search_fields = [
        "name",
        "description",
    ]

    ordering_fields = [
        "name",
        "amount",
        "due_date",
        "created_at",
        "updated_at",
    ]

    ordering = ["-due_date"]


class StudentFeeViewSet(viewsets.ModelViewSet):
    serializer_class = StudentFeeSerializer
    permission_classes = [StudentFeePermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = StudentFeeFilter

    search_fields = [
        "student__student_id",
        "fee_structure__name",
    ]

    ordering_fields = [
        "amount",
        "paid_amount",
        "due_amount",
        "due_date",
        "created_at",
        "updated_at",
    ]

    ordering = ["-due_date"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return StudentFee.objects.none()

        user = self.request.user

        if user.role in (
            UserRole.ADMIN,
            UserRole.ACCOUNTANT,
        ):
            return StudentFee.objects.all()

        if user.role == UserRole.STUDENT:
            return StudentFee.objects.filter(
                student__user=user
            )

        return StudentFee.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):

    serializer_class = PaymentSerializer
    permission_classes = [PaymentPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = PaymentFilter

    search_fields = [
        "transaction_id",
        "remarks",
        "student_fee__student__student_id",
    ]

    ordering_fields = [
        "amount",
        "payment_date",
        "created_at",
        "updated_at",
    ]

    ordering = ["-payment_date"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Payment.objects.none()

        user = self.request.user

        if user.role in (
            UserRole.ADMIN,
            UserRole.ACCOUNTANT,
        ):
            return Payment.objects.all()

        if user.role == UserRole.STUDENT:
            return Payment.objects.filter(
                student_fee__student__user=user
            )

        return Payment.objects.none()

    # =========================
    # Create Payment
    # =========================

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        # =========================
        # Get Student Fee
        # =========================

        student_fee = serializer.validated_data[
            "student_fee"
        ]

        payment_amount = Decimal(
            str(
                serializer.validated_data[
                    "amount"
                ]
            )
        )

        # =========================
        # Check Due Amount
        # =========================

        current_due = student_fee.due_amount

        if payment_amount <= 0:

            return Response(
                {
                    "detail": "Payment amount must be greater than 0."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment_amount > current_due:

            return Response(
                {
                    "detail": (
                        f"Payment amount cannot be greater "
                        f"than due amount ({current_due})."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # =========================
        # Create Payment
        # =========================

        payment = serializer.save()

        # =========================
        # Update Student Fee
        # =========================

        new_paid_amount = (
            student_fee.paid_amount
            + payment_amount
        )

        new_due_amount = (
            student_fee.amount
            - new_paid_amount
        )

        # =========================
        # Determine Status
        # =========================

        if new_due_amount == 0:

            new_status = "PAID"

        elif new_paid_amount > 0:

            new_status = "PARTIAL"

        else:

            new_status = "PENDING"

        student_fee.paid_amount = new_paid_amount
        student_fee.due_amount = new_due_amount
        student_fee.status = new_status

        student_fee.save(
            update_fields=[
                "paid_amount",
                "due_amount",
                "status",
                "updated_at",
            ]
        )

        # =========================
        # Student Information
        # =========================

        student = student_fee.student

        user = student.user

        # =========================
        # Email
        # =========================

        if user.email:

            student_name = (
                f"{user.first_name} "
                f"{user.last_name}"
            ).strip()

            subject = (
                "Payment Confirmation - "
                "School Management System"
            )

            message = f"""
Dear {student_name},

Your fee payment has been successfully received.

Payment Details
-------------------------

Student ID: {student.student_id}

Fee: {student_fee.fee_structure.name}

Amount Paid: {payment.amount}

Total Fee: {student_fee.amount}

Paid Amount: {student_fee.paid_amount}

Due Amount: {student_fee.due_amount}

Payment Date: {payment.payment_date}

Payment Method: {payment.payment_method}

Transaction ID: {payment.transaction_id or "N/A"}

Status: {student_fee.status}

Thank you.

School Management System
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        # =========================
        # Response
        # =========================

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )