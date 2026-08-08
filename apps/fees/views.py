from django_filters.rest_framework import DjangoFilterBackend
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