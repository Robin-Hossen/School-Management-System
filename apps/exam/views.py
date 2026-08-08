from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import (
    ExamPermission,
    ResultPermission,
)

from .filters import (
    ExamFilter,
    ExamSubjectFilter,
    ResultFilter,
)

from .models import Exam, ExamSubject, Result

from .serializers import (
    ExamSerializer,
    ExamSubjectSerializer,
    ResultSerializer,
)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [ExamPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ExamFilter

    search_fields = [
        "name",
        "exam_type",
    ]

    ordering_fields = [
        "name",
        "exam_type",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
    ]

    ordering = ["-start_date"]


class ExamSubjectViewSet(viewsets.ModelViewSet):
    queryset = ExamSubject.objects.all()
    serializer_class = ExamSubjectSerializer
    permission_classes = [ExamPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ExamSubjectFilter

    search_fields = [
        "exam__name",
        "subject__name",
    ]

    ordering_fields = [
        "exam_date",
        "start_time",
        "end_time",
        "total_marks",
        "created_at",
        "updated_at",
    ]

    ordering = ["exam_date", "start_time"]


class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [ResultPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ResultFilter

    search_fields = [
        "student__student_id",
        "grade",
        "remarks",
    ]

    ordering_fields = [
        "marks_obtained",
        "grade",
        "created_at",
        "updated_at",
    ]

    ordering = ["-marks_obtained"]

    def get_queryset(self):

        # Prevent drf-spectacular from accessing user.role
        # while generating the API schema.
        if getattr(self, "swagger_fake_view", False):
            return Result.objects.none()

        user = self.request.user

        if user.role == UserRole.ADMIN:
            return Result.objects.all()

        if user.role == UserRole.TEACHER:
            return Result.objects.all()

        if user.role == UserRole.STUDENT:
            return Result.objects.filter(
                student__user=user
            )

        return Result.objects.none()