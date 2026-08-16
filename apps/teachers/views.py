from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Teacher
from .serializers import TeacherSerializer

from apps.academic.models import TeachingAssignment
from apps.academic.serializers import TeachingAssignmentSerializer


class TeacherViewSet(viewsets.ModelViewSet):

    queryset = Teacher.objects.select_related("user").all()
    serializer_class = TeacherSerializer

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
    ]

    filterset_fields = [
        "designation",
    ]

    search_fields = [
        "teacher_id",
        "user__first_name",
        "user__last_name",
        "user__email",
    ]

    @action(
        detail=False,
        methods=["get"],
        url_path="my-classes",
        permission_classes=[IsAuthenticated]
    )
    def my_classes(self, request):

        try:
            teacher = request.user.teacher_profile

        except Teacher.DoesNotExist:

            return Response(
                {
                    "detail": "Teacher profile not found."
                },
                status=404
            )

        assignments = TeachingAssignment.objects.filter(
            teacher=teacher
        ).select_related(
            "subject",
            "class_name",
            "section",
            "academic_session"
        )

        serializer = TeachingAssignmentSerializer(
            assignments,
            many=True
        )

        return Response(serializer.data)