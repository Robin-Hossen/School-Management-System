from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.models import UserRole
from apps.accounts.permissions import AttendancePermission
from apps.academic.models import Enrollment, TeachingAssignment

from .filters import AttendanceFilter
from .models import Attendance
from .serializers import AttendanceSerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


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
            return Attendance.objects.filter(
                teaching_assignment__teacher__user=user
            )

        if user.role == UserRole.STUDENT:
            return Attendance.objects.filter(
                student__user=user
            )

        return Attendance.objects.none()
    @extend_schema(
    parameters=[
        OpenApiParameter(
            name="teaching_assignment",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="Teaching assignment ID"
        )
    ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="class-students"
    )
    def class_students(self, request):

        teaching_assignment_id = request.query_params.get(
            "teaching_assignment"
        )

        if not teaching_assignment_id:
            return Response(
                {
                    "detail": "teaching_assignment is required."
                },
                status=400
            )

        user = request.user

        if user.role != UserRole.TEACHER:
            return Response(
                {
                    "detail": "Only teachers can access class students."
                },
                status=403
            )

        assignment = TeachingAssignment.objects.filter(
            id=teaching_assignment_id,
            teacher__user=user
        ).first()

        if not assignment:
            return Response(
                {
                    "detail": "Teaching assignment not found."
                },
                status=404
            )

        enrollments = Enrollment.objects.filter(
            academic_session=assignment.academic_session,
            class_name=assignment.class_name,
            section=assignment.section,
            status=Enrollment.Status.ACTIVE
        ).select_related("student__user")

        data = [
            {
                "student_id": enrollment.student.id,
                "student_code": enrollment.student.student_id,
                "student_name": (
                    f"{enrollment.student.user.first_name} "
                    f"{enrollment.student.user.last_name}"
                    ).strip(),
            }
            for enrollment in enrollments
        ]

        return Response(data)