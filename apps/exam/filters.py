import django_filters

from .models import Exam, ExamSubject, Result


class ExamFilter(django_filters.FilterSet):

    class Meta:
        model = Exam
        fields = [
            "exam_type",
            "academic_session",
            "class_name",
            "start_date",
            "end_date",
        ]


class ExamSubjectFilter(django_filters.FilterSet):

    class Meta:
        model = ExamSubject
        fields = [
            "exam",
            "subject",
            "exam_date",
        ]


class ResultFilter(django_filters.FilterSet):

    # Filter by class
    class_name = django_filters.NumberFilter(
        field_name="exam_subject__exam__class_name_id"
    )

    # Filter by student
    student = django_filters.NumberFilter(
        field_name="student_id"
    )

    # Filter by exam subject
    exam_subject = django_filters.NumberFilter(
        field_name="exam_subject_id"
    )

    class Meta:
        model = Result
        fields = [
            "student",
            "exam_subject",
            "grade",
            "class_name",
        ]