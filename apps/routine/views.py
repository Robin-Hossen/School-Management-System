from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import RoutinePermission
from .models import Routine
from .serializers import RoutineSerializer


class RoutineViewSet(viewsets.ModelViewSet):

    serializer_class = RoutineSerializer
    permission_classes = [RoutinePermission]

    def get_queryset(self):

        queryset = Routine.objects.select_related(
            "teaching_assignment",
            "teaching_assignment__teacher",
            "teaching_assignment__teacher__user",
            "teaching_assignment__subject",
            "teaching_assignment__class_name",
            "teaching_assignment__section",
            "teaching_assignment__academic_session",
        )

        user = self.request.user

        # =========================
        # STUDENT
        # =========================
        if user.role == "STUDENT":

            try:
                student = user.student_profile

                enrollment = (
                    student.enrollments
                    .filter(status="ACTIVE")
                    .select_related(
                        "class_name",
                        "section",
                        "academic_session",
                    )
                    .first()
                )

                if not enrollment:
                    return Routine.objects.none()

                return queryset.filter(
                    teaching_assignment__class_name=enrollment.class_name,
                    teaching_assignment__section=enrollment.section,
                    teaching_assignment__academic_session=enrollment.academic_session,
                )

            except Exception:
                return Routine.objects.none()

        # =========================
        # TEACHER
        # =========================
        if user.role == "TEACHER":

            return queryset.filter(
                teaching_assignment__teacher__user=user
            )

        # =========================
        # ADMIN
        # =========================
        if user.role == "ADMIN":

            return queryset

        return Routine.objects.none()

    # =====================================================
    # TEACHER MY ROUTINE
    # =====================================================

    @action(
        detail=False,
        methods=["get"],
        url_path="my-routine",
    )
    def my_routine(self, request):

        if request.user.role != "TEACHER":
            return Response(
                {
                    "detail": "Only teachers can access their routine."
                },
                status=403,
            )

        routines = self.get_queryset().order_by(
            "day",
            "start_time"
        )

        serializer = self.get_serializer(
            routines,
            many=True
        )

        return Response(serializer.data)