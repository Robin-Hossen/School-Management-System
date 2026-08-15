from rest_framework import viewsets

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
        # ADMIN / TEACHER
        # =========================
        return queryset