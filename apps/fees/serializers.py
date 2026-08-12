from rest_framework import serializers

from .models import FeeStructure, StudentFee, Payment


class FeeStructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeeStructure
        fields = "__all__"


class StudentFeeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(
        source="student.user.get_full_name",
        read_only=True
    )

    student_id = serializers.CharField(
        source="student.student_id",
        read_only=True
    )

    fee_name = serializers.CharField(
        source="fee_structure.name",
        read_only=True
    )

    class_name = serializers.CharField(
        source="fee_structure.class_name.name",
        read_only=True
    )

    class Meta:
        model = StudentFee
        fields = [
            "id",
            "student",
            "student_name",
            "student_id",
            "fee_structure",
            "fee_name",
            "class_name",
            "amount",
            "paid_amount",
            "due_amount",
            "status",
            "due_date",
            "created_at",
            "updated_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"