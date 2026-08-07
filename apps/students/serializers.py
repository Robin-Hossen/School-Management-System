from rest_framework import serializers

from apps.accounts.models import CustomUser
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all()
    )
    class Meta:
        model=Student
        fields=[
            'id',
            'user',
            'student_id',
            'date_of_birth',
            'gender',
            'address',
            'guardian_name',
            'guardian_phone',
            'admission_date',
            'created_at',
            'updated_at'
        ]

        read_only_fields=['id','user','admission_date','created_at','updated_at']