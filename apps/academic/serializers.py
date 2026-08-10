from rest_framework import serializers
from .models import AcademicSession,Class,Subject,Section,Enrollment,TeachingAssignment

class AcademicSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model=AcademicSession
        fields="__all__"

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model=Class
        fields="__all__"

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model=Subject
        fields="__all__"


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Section
        fields="__all__"

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Enrollment
        fields="__all__"


class TeachingAssignmentSerializer(serializers.ModelSerializer):

    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source="subject.name",
        read_only=True
    )
    class_name_display = serializers.CharField(
        source="class_name.name",
        read_only=True
    )
    section_name = serializers.CharField(
        source="section.name",
        read_only=True
    )
    academic_session_name = serializers.CharField(
        source="academic_session.name",
        read_only=True
    )

    class Meta:
        model = TeachingAssignment
        fields = [
            "id",
            "teacher",
            "teacher_name",
            "subject",
            "subject_name",
            "class_name",
            "class_name_display",
            "section",
            "section_name",
            "academic_session",
            "academic_session_name",
            "created_at",
            "updated_at",
        ]

    def get_teacher_name(self, obj):
        user = obj.teacher.user

        return f"{user.first_name} {user.last_name}".strip()
