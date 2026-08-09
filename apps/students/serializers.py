from rest_framework import serializers

from apps.accounts.models import CustomUser
from .models import Student


class StudentSerializer(serializers.ModelSerializer):

    # Create করার সময় user data নেব
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )
    phone_number = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )

    # Response-এর জন্য
    user_info = serializers.SerializerMethodField()

    class Meta:
        model = Student

        fields = [
            "id",

            # User information
            "first_name",
            "last_name",
            "email",
            "password",
            "phone_number",

            # Student information
            "student_id",
            "date_of_birth",
            "gender",
            "address",
            "guardian_name",
            "guardian_phone",
            "admission_date",
            "created_at",
            "updated_at",

            # Response
            "user_info",
        ]

        read_only_fields = [
            "id",
            "user_info",
            "admission_date",
            "created_at",
            "updated_at",
        ]

    def get_user_info(self, obj):

        user = obj.user

        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": f"{user.first_name} {user.last_name}".strip(),
            "email": user.email,
            "phone_number": user.phone_number,
        }

    def create(self, validated_data):

        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        phone_number = validated_data.pop(
            "phone_number",
            ""
        )

        # Create CustomUser
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            role="STUDENT",
        )

        # Create Student
        student = Student.objects.create(
            user=user,
            **validated_data
        )

        return student