from rest_framework import serializers

from .models import FeeStructure, StudentFee, Payment


class FeeStructureSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeeStructure
        fields = "__all__"


class StudentFeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentFee
        fields = "__all__"


class PaymentSerializer(serializers.ModelSerializer):

    # ---------------------------------
    # Notification option
    # ---------------------------------

    NOTIFICATION_CHOICES = [
        ("NONE", "No Notification"),
        ("STUDENT", "Student"),
        ("GUARDIAN", "Guardian"),
        ("BOTH", "Student & Guardian"),
    ]

    notification = serializers.ChoiceField(
        choices=NOTIFICATION_CHOICES,
        write_only=True,
        required=False,
        default="NONE",
    )

    # ---------------------------------
    # Extra read-only information
    # ---------------------------------

    student_name = serializers.CharField(
        source="student_fee.student.user.get_full_name",
        read_only=True,
    )

    student_code = serializers.CharField(
        source="student_fee.student.student_id",
        read_only=True,
    )

    fee_name = serializers.CharField(
        source="student_fee.fee_structure.name",
        read_only=True,
    )

    class Meta:
        model = Payment

        fields = [
            "id",

            "student_fee",

            "student_name",
            "student_code",
            "fee_name",

            "amount",
            "payment_date",
            "payment_method",
            "transaction_id",
            "remarks",

            "notification",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "created_at",
            "updated_at",
        ]