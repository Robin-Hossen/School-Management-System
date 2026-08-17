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
        fields = "__all__"

        extra_fields = [
            "academic_session_name",
            "class_name_name",
        ]

    def to_representation(self, instance):

        data = super().to_representation(instance)

        data["academic_session_name"] = (
            instance.academic_session.name
        )

        data["class_name_name"] = (
            instance.class_name.name
        )

        return data


class ExamSubjectSerializer(serializers.ModelSerializer):

    exam_name = serializers.CharField(
        source="exam.name",
        read_only=True
    )

    exam_type = serializers.CharField(
        source="exam.exam_type",
        read_only=True
    )

    academic_session_name = serializers.CharField(
        source="exam.academic_session.name",
        read_only=True
    )

    subject_name = serializers.CharField(
        source="subject.name",
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

    class Meta:
        model = ExamSubject

        fields = [
            "id",

            "exam",
            "exam_name",
            "exam_type",
            "academic_session_name",

            "subject",
            "subject_name",

            "teaching_assignment",

            "class_name",
            "section_name",

            "exam_date",
            "start_time",
            "end_time",
            "total_marks",

            "created_at",
            "updated_at",
        ]





class ResultSerializer(serializers.ModelSerializer):

    student_code = serializers.CharField(
        source="student.student_id",
        read_only=True
    )

    student_name = serializers.SerializerMethodField()

    exam = serializers.IntegerField(
        source="exam_subject.exam.id",
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

    class_name = serializers.IntegerField(
        source="exam_subject.exam.class_name.id",
        read_only=True
    )

    class_name_name = serializers.CharField(
        source="exam_subject.exam.class_name.name",
        read_only=True
    )

    grade_point = serializers.DecimalField(
        max_digits=3,
        decimal_places=2,
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

            "exam",
            "exam_name",
            "subject_name",

            "class_name",
            "class_name_name",

            "marks_obtained",
            "total_marks",

            "grade",
            "grade_point",

            "remarks",

            "created_at",
            "updated_at",
        ]

    def get_student_name(self, obj):

        user = obj.student.user

        return (
            f"{user.first_name} "
            f"{user.last_name}"
        ).strip()
# =========================================================
# Result Entry Serializers
# =========================================================
class ResultEntryItemSerializer(serializers.Serializer):
    student = serializers.IntegerField()
    marks_obtained = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )
    remarks = serializers.CharField(
        required=False,
        allow_blank=True,
        default=""
    )


class EnterResultsSerializer(serializers.Serializer):
    exam_subject = serializers.IntegerField()

    results = ResultEntryItemSerializer(
        many=True
    )        