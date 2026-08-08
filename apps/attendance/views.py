from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import AttendancePermission

from .filters import AttendanceFilter
from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [AttendancePermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = AttendanceFilter

    search_fields = [
        "remarks",
    ]

    ordering_fields = [
        "date",
        "created_at",
        "updated_at",
        "status",
    ]

    ordering = ["-date"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Attendance.objects.none()

        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Attendance.objects.all()

        if user.role == UserRole.TEACHER:
            return Attendance.objects.all()

        if user.role == UserRole.STUDENT:
            return Attendance.objects.filter(
                student__user=user
            )

        return Attendance.objects.none()