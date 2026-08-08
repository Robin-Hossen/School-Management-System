from rest_framework import viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import (
    ExamPermission,
    ResultPermission,
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


class ExamSubjectViewSet(viewsets.ModelViewSet):
    queryset = ExamSubject.objects.all()
    serializer_class = ExamSubjectSerializer
    permission_classes = [ExamPermission]


class ResultViewSet(viewsets.ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [ResultPermission]

    def get_queryset(self):
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