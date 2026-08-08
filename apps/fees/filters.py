import django_filters

from .models import FeeStructure, StudentFee, Payment


class FeeStructureFilter(django_filters.FilterSet):
    class Meta:
        model = FeeStructure
        fields = [
            "academic_session",
            "class_name",
            "due_date",
        ]


class StudentFeeFilter(django_filters.FilterSet):
    class Meta:
        model = StudentFee
        fields = [
            "student",
            "fee_structure",
            "status",
            "due_date",
        ]


class PaymentFilter(django_filters.FilterSet):
    class Meta:
        model = Payment
        fields = [
            "student_fee",
            "payment_date",
            "payment_method",
        ]