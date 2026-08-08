from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Student
from .serializers import StudentSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_fields = [
        "gender",
    ]

    search_fields = [
        "student_id",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    ordering_fields = [
        "student_id",
        "date_of_birth",
        "created_at",
    ]

    ordering = ["id"]