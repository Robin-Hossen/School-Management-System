import django_filters

from .models import Routine


class RoutineFilter(django_filters.FilterSet):

    class Meta:
        model = Routine

        fields = [
            "teaching_assignment",
            "day",
            "room_number",
            "start_time",
            "end_time",
        ]