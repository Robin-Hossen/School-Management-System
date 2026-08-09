from datetime import date

from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.academic.models import Class, Subject
from apps.attendance.models import Attendance
from apps.fees.models import StudentFee
from apps.exam.models import Exam
from apps.notice.models import Notice


class AdminDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "ADMIN":
            return Response(
                {"detail": "You do not have permission to access this dashboard."},
                status=403
            )

        # =========================
        # Attendance
        # =========================

        present = Attendance.objects.filter(
            date=date.today(),
            status="PRESENT"
        ).count()

        absent = Attendance.objects.filter(
            date=date.today(),
            status="ABSENT"
        ).count()

        late = Attendance.objects.filter(
            date=date.today(),
            status="LATE"
        ).count()

        # =========================
        # Basic Statistics
        # =========================

        total_students = Student.objects.count()
        total_teachers = Teacher.objects.count()
        total_classes = Class.objects.count()
        total_subjects = Subject.objects.count()

        # =========================
        # Upcoming Exams
        # =========================

        upcoming_exams = Exam.objects.filter(
            start_date__gte=date.today()
        ).order_by("start_date")[:5]

        # =========================
        # Recent Notices
        # =========================

        recent_notices = Notice.objects.filter(
        is_active=True
        ).order_by("-publish_date")[:5] 

        # =========================
        # Fee Statistics
        # =========================

        total_fee = StudentFee.objects.aggregate(
            total=Sum("amount")
        )["total"] or 0

        total_paid = StudentFee.objects.aggregate(
            total=Sum("paid_amount")
        )["total"] or 0

        total_due = StudentFee.objects.aggregate(
            total=Sum("due_amount")
        )["total"] or 0

        # =========================
        # Response
        # =========================

        return Response({

            "students": {
                "total": total_students
            },

            "teachers": {
                "total": total_teachers
            },

            "classes": {
                "total": total_classes
            },

            "subjects": {
                "total": total_subjects
            },

            "fees": {
                "total": total_fee,
                "paid": total_paid,
                "due": total_due
            },

            "attendance": {
                "present": present,
                "absent": absent,
                "late": late
            },

            "upcoming_exams": [
                {
                    "id": exam.id,
                    "name": exam.name,
                    "exam_type": exam.exam_type,
                    "start_date": exam.start_date,
                    "end_date": exam.end_date,
                    "class_name": exam.class_name.name,
                }
                for exam in upcoming_exams
            ],

            "recent_notices": [
                {
                    "id": notice.id,
                    "title": notice.title,
                    "content": notice.content,
                    "publish_date": notice.publish_date,
                    "target_audience": notice.target_audience,
                }
                for notice in recent_notices
            ],
        })