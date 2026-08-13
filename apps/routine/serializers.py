from rest_framework import serializers

from .models import Routine


class RoutineSerializer(serializers.ModelSerializer):

    teacher_name = serializers.SerializerMethodField()

    subject_name = serializers.CharField(
        source="teaching_assignment.subject.name",
        read_only=True
    )

    class_name_display = serializers.CharField(
        source="teaching_assignment.class_name.name",
        read_only=True
    )

    section_name = serializers.CharField(
        source="teaching_assignment.section.name",
        read_only=True
    )

    academic_session_name = serializers.CharField(
        source="teaching_assignment.academic_session.name",
        read_only=True
    )

    class Meta:
        model = Routine

        fields = [
            "id",
            "teaching_assignment",

            "teacher_name",
            "subject_name",
            "class_name_display",
            "section_name",
            "academic_session_name",

            "day",
            "start_time",
            "end_time",
            "room_number",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "teacher_name",
            "subject_name",
            "class_name_display",
            "section_name",
            "academic_session_name",
            "created_at",
            "updated_at",
        ]

    def get_teacher_name(self, obj):
        user = obj.teaching_assignment.teacher.user

        return f"{user.first_name} {user.last_name}".strip()