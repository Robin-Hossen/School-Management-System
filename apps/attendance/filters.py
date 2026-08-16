import django_filters

from .models import Attendance


class AttendanceFilter(django_filters.FilterSet):

    class Meta:
        model = Attendance

        fields = [
            "date",
            "status",
            "student",
            "enrollment",
            "teaching_assignment",
        ]