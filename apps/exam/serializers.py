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

    exam_name = serializers.CharField(
        source="exam.name",
        read_only=True
    )

    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True
    )

    class Meta:
        model = ExamSubject
        fields = [
            "id",

            "exam",
            "exam_name",

            "subject",
            "subject_name",

            "exam_date",
            "start_time",
            "end_time",
            "total_marks",

            "created_at",
            "updated_at",
        ]


class ResultSerializer(serializers.ModelSerializer):

    class Meta:
        model = Result
        fields = "__all__"