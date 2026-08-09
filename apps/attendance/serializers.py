from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = "__all__"

class AttendanceStudentSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    student_code = serializers.CharField()
    student_name = serializers.CharField()
    status = serializers.CharField()        

class TakeAttendanceSerializer(serializers.Serializer):

    teaching_assignment = serializers.IntegerField()

    date = serializers.DateField()

    attendance = serializers.ListField(
        child=serializers.DictField()
    )    