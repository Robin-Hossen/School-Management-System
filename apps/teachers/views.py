from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Teacher
from .serializers import TeacherSerializer


class TeacherViewSet(viewsets.ModelViewSet):

    queryset = Teacher.objects.select_related("user").all()
    serializer_class = TeacherSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]

    # Filter
    filterset_fields = [
        "designation",
    ]

    # Search
    search_fields = [
        "teacher_id",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]