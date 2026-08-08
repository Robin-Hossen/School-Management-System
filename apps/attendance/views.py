from rest_framework import viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import AttendancePermission

from .models import Attendance
from .serializers import AttendanceSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [AttendancePermission]

    def get_queryset(self):
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