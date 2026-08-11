from rest_framework import serializers

from .models import Exam, ExamSubject, Result


class ExamSerializer(serializers.ModelSerializer):

    academic_session_name = serializers.CharField(
        source="academic_session.name",
        read_only=True
    )

    class_name_name = serializers.CharField(
        source="class_name.name",
        read_only=True
    )

    class Meta:
        model = Exam
        fields = [
            "id",
            "name",
            "exam_type",

            "academic_session",
            "academic_session_name",

            "class_name",
            "class_name_name",

            "start_date",
            "end_date",

            "created_at",
            "updated_at",
        ]


class ExamSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExamSubject
        fields = "__all__"


class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = "__all__"