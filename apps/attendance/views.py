from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from apps.accounts.models import UserRole
from apps.accounts.permissions import AttendancePermission
from apps.academic.models import Enrollment, TeachingAssignment

from .filters import AttendanceFilter
from .models import Attendance
from .serializers import AttendanceSerializer, TakeAttendanceSerializer

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)


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

    # =========================================================
    # QUERYSET
    # =========================================================

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Attendance.objects.none()

        user = self.request.user

        queryset = Attendance.objects.select_related(
            "student__user",
            "enrollment",
            "teaching_assignment__teacher__user",
            "teaching_assignment__subject",
            "teaching_assignment__class_name",
            "teaching_assignment__section",
            "teaching_assignment__academic_session",
        )

        # ADMIN
        if user.role == UserRole.ADMIN:
            return queryset

        # TEACHER
        if user.role == UserRole.TEACHER:
            return queryset.filter(
                teaching_assignment__teacher__user=user
            )

        # STUDENT
        if user.role == UserRole.STUDENT:
            return queryset.filter(
                student__user=user
            )

        return Attendance.objects.none()

    # =========================================================
    # GET CLASS STUDENTS
    # =========================================================

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="teaching_assignment",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Teaching assignment ID",
            )
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="class-students",
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
                status=400,
            )

        user = request.user

        # Only teacher can access class students
        if user.role != UserRole.TEACHER:
            return Response(
                {
                    "detail": "Only teachers can access class students."
                },
                status=403,
            )

        # Verify teaching assignment belongs to teacher
        assignment = TeachingAssignment.objects.filter(
            id=teaching_assignment_id,
            teacher__user=user,
        ).select_related(
            "academic_session",
            "class_name",
            "section",
        ).first()

        if not assignment:
            return Response(
                {
                    "detail": "Teaching assignment not found."
                },
                status=404,
            )

        # Get active students
        enrollments = Enrollment.objects.filter(
            academic_session=assignment.academic_session,
            class_name=assignment.class_name,
            section=assignment.section,
            status=Enrollment.Status.ACTIVE,
        ).select_related(
            "student__user"
        )

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

    # =========================================================
    # TAKE ATTENDANCE
    # =========================================================

    @action(
        detail=False,
        methods=["post"],
        url_path="take-attendance",
    )
    def take_attendance(self, request):

        # Only teacher can take attendance
        if request.user.role != UserRole.TEACHER:
            return Response(
                {
                    "detail": "Only teachers can take attendance."
                },
                status=403,
            )

        # Validate request data
        serializer = TakeAttendanceSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        teaching_assignment_id = (
            serializer.validated_data[
                "teaching_assignment"
            ]
        )

        attendance_date = (
            serializer.validated_data[
                "date"
            ]
        )

        attendance_data = (
            serializer.validated_data[
                "attendance"
            ]
        )

        # =====================================================
        # Verify Teaching Assignment
        # =====================================================

        assignment = TeachingAssignment.objects.filter(
            id=teaching_assignment_id,
            teacher__user=request.user,
        ).first()

        if not assignment:
            return Response(
                {
                    "detail": "Teaching assignment not found."
                },
                status=404,
            )

        # =====================================================
        # Get Active Students
        # =====================================================

        enrollments = Enrollment.objects.filter(
            academic_session=assignment.academic_session,
            class_name=assignment.class_name,
            section=assignment.section,
            status=Enrollment.Status.ACTIVE,
        )

        valid_student_ids = set(
            enrollments.values_list(
                "student_id",
                flat=True,
            )
        )

        # =====================================================
        # Validate Students
        # =====================================================

        for item in attendance_data:

            student_id = item.get(
                "student_id"
            )

            status = item.get(
                "status"
            )

            # Check student belongs to class
            if student_id not in valid_student_ids:
                return Response(
                    {
                        "detail": (
                            f"Student {student_id} "
                            "does not belong to this class."
                        )
                    },
                    status=400,
                )

            # Check attendance status
            if status not in [
                "PRESENT",
                "ABSENT",
                "LATE",
                "EXCUSED",
            ]:
                return Response(
                    {
                        "detail": (
                            f"Invalid attendance status "
                            f"for student {student_id}."
                        )
                    },
                    status=400,
                )

        # =====================================================
        # Save Attendance
        # =====================================================

        saved_attendance = []

        with transaction.atomic():

            for item in attendance_data:

                student_id = item[
                    "student_id"
                ]

                status = item[
                    "status"
                ]

                enrollment = enrollments.get(
                    student_id=student_id
                )

                attendance, created_new = (
                    Attendance.objects.update_or_create(
                        student_id=student_id,
                        enrollment=enrollment,
                        teaching_assignment=assignment,
                        date=attendance_date,
                        defaults={
                            "status": status
                        },
                    )
                )

                saved_attendance.append(
                    attendance
                )

        # =====================================================
        # Response
        # =====================================================

        return Response(
            {
                "message": "Attendance saved successfully.",
                "count": len(saved_attendance),
                "attendance": AttendanceSerializer(
                    saved_attendance,
                    many=True,
                ).data,
            },
            status=200,
        )