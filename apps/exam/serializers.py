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

    student_name = serializers.SerializerMethodField()

    student_code = serializers.CharField(
        source="student.student_id",
        read_only=True
    )

    exam_name = serializers.CharField(
        source="exam_subject.exam.name",
        read_only=True
    )

    subject_name = serializers.CharField(
        source="exam_subject.subject.name",
        read_only=True
    )

    total_marks = serializers.IntegerField(
        source="exam_subject.total_marks",
        read_only=True
    )

    class Meta:
        model = Result

        fields = [
            "id",

            "student",
            "student_code",
            "student_name",

            "exam_subject",
            "exam_name",
            "subject_name",

            "marks_obtained",
            "total_marks",

            "grade",
            "grade_point",

            "remarks",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "grade",
            "grade_point",
            "created_at",
            "updated_at",
        ]

    def get_student_name(self, obj):

        user = obj.student.user

        return (
            f"{user.first_name} "
            f"{user.last_name}"
        ).strip()