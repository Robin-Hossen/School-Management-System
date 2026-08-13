from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets


from apps.accounts.permissions import RoutinePermission

from .models import Routine
from .serializers import RoutineSerializer


class RoutineViewSet(viewsets.ModelViewSet):

    serializer_class = RoutineSerializer
    permission_classes = [RoutinePermission]

    queryset = Routine.objects.select_related(
        "teaching_assignment",
        "teaching_assignment__teacher",
        "teaching_assignment__teacher__user",
        "teaching_assignment__subject",
        "teaching_assignment__class_name",
        "teaching_assignment__section",
        "teaching_assignment__academic_session",
    )