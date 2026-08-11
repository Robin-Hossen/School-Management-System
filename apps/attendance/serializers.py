from rest_framework import serializers
from apps.academic.models import TeachingAssignment
from .models import Attendance


class AttendanceItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=Attendance.STATUS_CHOICES)


class TakeAttendanceSerializer(serializers.Serializer):
    teaching_assignment = serializers.PrimaryKeyRelatedField(
        queryset=TeachingAssignment.objects.all()
    )
    date = serializers.DateField()
    attendance = serializers.ListField(child=AttendanceItemSerializer())


class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_code = serializers.CharField(
        source="student.student_id",
        read_only=True
    )

    subject_name = serializers.CharField(
        source="teaching_assignment.subject.name",
        read_only=True
    )

    class_name = serializers.CharField(
        source="teaching_assignment.class_name.name",
        read_only=True
    )

    section_name = serializers.CharField(
        source="teaching_assignment.section.name",
        read_only=True
    )

    session_name = serializers.CharField(
        source="teaching_assignment.academic_session.name",
        read_only=True
    )

    class Meta:
        model = Attendance
        fields = [
            "id",

            "student",
            "student_name",
            "student_code",

            "enrollment",
            "teaching_assignment",

            "subject_name",
            "class_name",
            "section_name",
            "session_name",

            "date",
            "status",
            "remarks",

            "created_at",
            "updated_at",
        ]

    def get_student_name(self, obj):
        user = obj.student.user

        return f"{user.first_name} {user.last_name}".strip()