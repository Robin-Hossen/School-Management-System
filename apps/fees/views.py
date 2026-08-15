from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction

from decimal import Decimal
from django.utils import timezone

import stripe

from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters, viewsets
from rest_framework.decorators import action

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

from .models import (
    FeeStructure,
    StudentFee,
    Payment,
)

from .serializers import (
    FeeStructureSerializer,
    StudentFeeSerializer,
    PaymentSerializer,
)


# ============================================================
# Stripe Configuration
# ============================================================

stripe.api_key = settings.STRIPE_SECRET_KEY


# ============================================================
# Fee Structure
# ============================================================

class FeeStructureViewSet(viewsets.ModelViewSet):

    queryset = FeeStructure.objects.all()

    serializer_class = FeeStructureSerializer

    permission_classes = [
        FeeStructurePermission
    ]

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


# ============================================================
# Student Fee
# ============================================================

class StudentFeeViewSet(viewsets.ModelViewSet):

    serializer_class = StudentFeeSerializer

    permission_classes = [
        StudentFeePermission
    ]

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

        if getattr(
            self,
            "swagger_fake_view",
            False
        ):
            return StudentFee.objects.none()

        user = self.request.user

        # Admin / Accountant
        if user.role in (
            UserRole.ADMIN,
            UserRole.ACCOUNTANT,
        ):

            return StudentFee.objects.all()

        # Student
        if user.role == UserRole.STUDENT:

            return StudentFee.objects.filter(
                student__user=user
            )

        return StudentFee.objects.none()


# ============================================================
# Payment
# ============================================================

class PaymentViewSet(viewsets.ModelViewSet):

    serializer_class = PaymentSerializer

    permission_classes = [
        PaymentPermission
    ]

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

    # ========================================================
    # Queryset
    # ========================================================

    def get_queryset(self):

        if getattr(
            self,
            "swagger_fake_view",
            False
        ):
            return Payment.objects.none()

        user = self.request.user

        # Admin / Accountant
        if user.role in (
            UserRole.ADMIN,
            UserRole.ACCOUNTANT,
        ):

            return Payment.objects.all()

        # Student
        if user.role == UserRole.STUDENT:

            return Payment.objects.filter(
                student_fee__student__user=user
            )

        return Payment.objects.none()

    # ========================================================
    # Manual Payment
    # ========================================================

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        # ----------------------------------------------------
        # Student Fee
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Check Amount
        # ----------------------------------------------------

        current_due = student_fee.due_amount

        if payment_amount <= 0:

            return Response(
                {
                    "detail":
                    "Payment amount must be greater than 0."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if payment_amount > current_due:

            return Response(
                {
                    "detail": (
                        "Payment amount cannot be "
                        f"greater than due amount "
                        f"({current_due})."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Create Payment & Update Student Fee (Atomic)
        # ----------------------------------------------------

        with transaction.atomic():

            payment = serializer.save()

            # ------------------------------------------------
            # Update Student Fee
            # ------------------------------------------------

            new_paid_amount = (
                student_fee.paid_amount
                + payment_amount
            )

            new_due_amount = (
                student_fee.amount
                - new_paid_amount
            )

            # ------------------------------------------------
            # Determine Status
            # ------------------------------------------------

            if new_due_amount == 0:

                new_status = "PAID"

            elif new_paid_amount > 0:

                new_status = "PARTIAL"

            else:

                new_status = "PENDING"

            student_fee.paid_amount = (
                new_paid_amount
            )

            student_fee.due_amount = (
                new_due_amount
            )

            student_fee.status = new_status

            student_fee.save(
                update_fields=[
                    "paid_amount",
                    "due_amount",
                    "status",
                    "updated_at",
                ]
            )

        # ----------------------------------------------------
        # Student Information
        # ----------------------------------------------------

        student = student_fee.student

        user = student.user

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

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

Transaction ID:
{payment.transaction_id or "N/A"}

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

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    # ========================================================
    # Stripe Checkout
    # ========================================================

    @action(
        detail=False,
        methods=["post"],
        url_path="create-checkout"
    )
    def create_checkout(self, request):

        user = request.user

        # ----------------------------------------------------
        # Only Student Can Pay Online
        # ----------------------------------------------------

        if user.role != UserRole.STUDENT:

            return Response(
                {
                    "detail":
                    "Only students can make online payments."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------------------------
        # Student Fee ID
        # ----------------------------------------------------

        student_fee_id = request.data.get(
            "student_fee_id"
        )

        if not student_fee_id:

            return Response(
                {
                    "detail":
                    "student_fee_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Get Student Fee
        # ----------------------------------------------------

        try:

            student_fee = StudentFee.objects.select_related(
                "student",
                "student__user",
                "fee_structure",
            ).get(
                id=student_fee_id,
                student__user=user,
            )

        except StudentFee.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Student fee not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ----------------------------------------------------
        # Check Due Amount
        # ----------------------------------------------------

        if student_fee.due_amount <= 0:

            return Response(
                {
                    "detail":
                    "This fee has already been paid."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Convert BDT to Paisa
        # ----------------------------------------------------

        amount_in_paisa = int(
            student_fee.due_amount * 100
        )

        # ----------------------------------------------------
        # Create Stripe Checkout Session
        # ----------------------------------------------------

        try:

            checkout_session = stripe.checkout.Session.create(

                mode="payment",

                payment_method_types=[
                    "card"
                ],

                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",

                            "product_data": {
                                "name":
                                    student_fee
                                    .fee_structure
                                    .name,

                                "description": (
                                    f"Student ID: "
                                    f"{student_fee.student.student_id}"
                                ),
                            },

                            "unit_amount":
                                amount_in_paisa,
                        },

                        "quantity": 1,
                    }
                ],

                metadata={
                    "student_fee_id":
                        str(student_fee.id),

                    "student_id":
                        str(student_fee.student.id),
                },

                success_url=(
                    "http://localhost:5173/"
                    "student/fees/payment-success"
                    "?session_id={CHECKOUT_SESSION_ID}"
                ),

                cancel_url=(
                    "http://localhost:5173/"
                    "student/fees"
                ),
            )

            return Response(
                {
                    "checkout_url":
                        checkout_session.url,

                    "session_id":
                        checkout_session.id,
                },
                status=status.HTTP_201_CREATED
            )

        except stripe.error.StripeError as e:

            return Response(
                {
                    "detail":
                        f"Stripe error: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return Response(
                {
                    "detail":
                        f"Unable to create checkout session: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    # ========================================================
    # Stripe Payment Verification
    # ========================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="verify-payment"
    )
    def verify_payment(self, request):

        user = request.user

        # ----------------------------------------------------
        # Only Student
        # ----------------------------------------------------

        if user.role != UserRole.STUDENT:

            return Response(
                {
                    "detail":
                    "Only students can verify online payments."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------------------------
        # Get Session ID
        # ----------------------------------------------------

        session_id = request.query_params.get(
            "session_id"
        )

        if not session_id:

            return Response(
                {
                    "detail":
                    "session_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Retrieve Stripe Session
        # ----------------------------------------------------

        try:

            checkout_session = (
                stripe.checkout.Session.retrieve(
                session_id
            )
            )

        except stripe.error.StripeError as e:

            return Response(
                {
                    "detail":
                        f"Stripe error: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Check Payment Status
        # ----------------------------------------------------

        if checkout_session.payment_status != "paid":

            return Response(
                {
                    "detail":
                        "Payment has not been completed.",
                    "payment_status":
                        checkout_session.payment_status,
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Get student fee ID from Metadata
        # ----------------------------------------------------

        metadata = checkout_session.metadata or {}
        
        if isinstance(metadata, dict):
            student_fee_id = metadata.get("student_fee_id")
        else:
            student_fee_id = getattr(metadata, "student_fee_id", None)

        if not student_fee_id:
            return Response(
                {
                    "detail": "Student fee information is missing."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        

        # ----------------------------------------------------
        # Get Student Fee
        # ----------------------------------------------------

        try:

            student_fee = StudentFee.objects.select_related(
                "student",
                "student__user",
                "fee_structure",
            ).get(
                id=student_fee_id,
                student__user=user,
            )

        except StudentFee.DoesNotExist:

            return Response(
                {
                    "detail":
                    "Student fee not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # ----------------------------------------------------
        # Prevent Duplicate Payment
        # ----------------------------------------------------

        existing_payment = Payment.objects.filter(
            transaction_id=checkout_session.payment_intent
        ).first()

        if existing_payment:

            return Response(
                {
                    "detail":
                    "Payment has already been recorded.",
                    "payment_id":
                        existing_payment.id,
                    "status":
                        "already_recorded",
                },
                status=status.HTTP_200_OK
            )

        # ----------------------------------------------------
        # Amount Paid
        # ----------------------------------------------------

        payment_amount = Decimal(
            checkout_session.amount_total
        ) / Decimal("100")

        # ----------------------------------------------------
        # Check Due Amount
        # ----------------------------------------------------

        if payment_amount > student_fee.due_amount:

            return Response(
                {
                    "detail":
                    "Payment amount is greater than the current due amount."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ----------------------------------------------------
        # Create Payment & Update Student Fee (Atomic)
        # ----------------------------------------------------

        with transaction.atomic():

            payment = Payment.objects.create(

                student_fee=student_fee,

                amount=payment_amount,

                payment_date=timezone.now().date(),

                payment_method="CARD",

                transaction_id=(
                    checkout_session.payment_intent
                ),

                remarks="Stripe online payment",
            )

            # ------------------------------------------------
            # Update Student Fee
            # ------------------------------------------------

            new_paid_amount = (
                student_fee.paid_amount
                + payment_amount
            )

            new_due_amount = (
                student_fee.amount
                - new_paid_amount
            )

            if new_due_amount <= 0:

                new_due_amount = Decimal("0.00")

                new_status = "PAID"

            elif new_paid_amount > 0:

                new_status = "PARTIAL"

            else:

                new_status = "PENDING"

            student_fee.paid_amount = (
                new_paid_amount
            )

            student_fee.due_amount = (
                new_due_amount
            )

            student_fee.status = new_status

            student_fee.save(
                update_fields=[
                    "paid_amount",
                    "due_amount",
                    "status",
                    "updated_at",
                ]
            )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return Response(
            {
                "detail":
                    "Payment verified successfully.",

                "payment_id":
                    payment.id,

                "student_fee_id":
                    student_fee.id,

                "amount":
                    str(payment_amount),

                "paid_amount":
                    str(student_fee.paid_amount),

                "due_amount":
                    str(student_fee.due_amount),

                "status":
                    student_fee.status,

                "transaction_id":
                    payment.transaction_id,
            },
            status=status.HTTP_200_OK
        )