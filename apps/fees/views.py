from rest_framework import viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import (
    FeeStructurePermission,
    StudentFeePermission,
    PaymentPermission,
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


class StudentFeeViewSet(viewsets.ModelViewSet):
    serializer_class = StudentFeeSerializer
    permission_classes = [StudentFeePermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return StudentFee.objects.all()

        if user.role == UserRole.ACCOUNTANT:
            return StudentFee.objects.all()

        if user.role == UserRole.STUDENT:
            return StudentFee.objects.filter(
                student__user=user
            )

        return StudentFee.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [PaymentPermission]

    def get_queryset(self):
        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Payment.objects.all()

        if user.role == UserRole.ACCOUNTANT:
            return Payment.objects.all()

        if user.role == UserRole.STUDENT:
            return Payment.objects.filter(
                student_fee__student__user=user
            )

        return Payment.objects.none()