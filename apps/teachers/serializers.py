from rest_framework import serializers
from .models import Teacher


class TeacherSerializer(serializers.ModelSerializer):

    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "user",
            "user_info",
            "teacher_id",
            "designation",
            "qualification",
            "image",
            "phone_number",
            "joining_date",
            "address",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "user_info",
            "created_at",
            "updated_at",
        ]

    def get_user_info(self, obj):
        return {
            "id": obj.user.id,
            "first_name": obj.user.first_name,
            "last_name": obj.user.last_name,
            "full_name": f"{obj.user.first_name} {obj.user.last_name}".strip(),
            "email": obj.user.email,
            "phone_number": getattr(obj.user, "phone_number", ""),
        }