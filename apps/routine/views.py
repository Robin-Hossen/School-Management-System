from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import RoutinePermission

from .filters import RoutineFilter
from .models import Routine
from .serializers import RoutineSerializer


class RoutineViewSet(viewsets.ModelViewSet):
    serializer_class = RoutineSerializer
    permission_classes = [RoutinePermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = RoutineFilter

    search_fields = [
        "room_number",
        "day",
    ]

    ordering_fields = [
        "day",
        "start_time",
        "end_time",
        "created_at",
    ]

    ordering = [
        "day",
        "start_time",
    ]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Routine.objects.none()

        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Routine.objects.all()

        if user.role == UserRole.TEACHER:
            return Routine.objects.filter(
                teaching_assignment__teacher__user=user
            )

        if user.role == UserRole.STUDENT:
            return Routine.objects.filter(
                teaching_assignment__class_name__enrollments__student__user=user
            ).distinct()

        return Routine.objects.none()