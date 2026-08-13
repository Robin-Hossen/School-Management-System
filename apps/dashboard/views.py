from datetime import date

from django.db.models import Sum,Avg

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.students.models import Student
from apps.teachers.models import Teacher
from apps.academic.models import TeachingAssignment,Enrollment
from apps.academic.models import Class, Subject
from apps.attendance.models import Attendance
from apps.fees.models import StudentFee
from apps.exam.models import Exam,Result
from apps.notice.models import Notice
from apps.routine.models import Routine


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



class TeacherDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            teacher = request.user.teacher_profile
        except Teacher.DoesNotExist:
            return Response(
                {"detail": "Teacher profile not found."},
                status=404
            )

        assignments = TeachingAssignment.objects.filter(
            teacher=teacher
        ).select_related(
            "subject",
            "class_name",
            "section",
            "academic_session"
        )

        # Total classes
        total_classes = assignments.values(
            "class_name",
            "section"
        ).distinct().count()

        # Total subjects
        total_subjects = assignments.values(
            "subject"
        ).distinct().count()

        # Today's attendance
        today_attendance = Attendance.objects.filter(
            teaching_assignment__in=assignments,
            date=date.today()
        )

        present = today_attendance.filter(
            status="PRESENT"
        ).count()

        absent = today_attendance.filter(
            status="ABSENT"
        ).count()

        late = today_attendance.filter(
            status="LATE"
        ).count()

        excused = today_attendance.filter(
            status="EXCUSED"
        ).count()

        # Today's routine
        today_name = date.today().strftime("%A").upper()

        today_routine = []

        for assignment in assignments:

            routines = assignment.routines.filter(
                day=today_name
            ).order_by("start_time")

            for routine in routines:

                today_routine.append({
                    "id": routine.id,
                    "subject_name": assignment.subject.name,
                    "class_name": assignment.class_name.name,
                    "section_name": assignment.section.name,
                    "start_time": routine.start_time,
                    "end_time": routine.end_time,
                    "room_number": routine.room_number,
                })

        # Upcoming exams
        upcoming_exams = Exam.objects.filter(
            start_date__gte=date.today()
        ).order_by("start_date")[:5]

        # Recent notices
        recent_notices = Notice.objects.filter(
            is_active=True
        ).order_by("-publish_date")[:5]

        # Teacher information
        user = teacher.user

        teacher_name = f"{user.first_name} {user.last_name}".strip()

        if not teacher_name:
            teacher_name = user.username

        return Response({

            "teacher": {
                "id": teacher.id,
                "teacher_id": teacher.teacher_id,
                "name": teacher_name,
                "designation": teacher.designation,
            },

            "classes": {
                "total": total_classes,
            },

            "subjects": {
                "total": total_subjects,
            },

            "attendance": {
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
            },

            "today_routine": today_routine,

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

class StudentDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        # =========================
        # Check Role
        # =========================

        if request.user.role != "STUDENT":
            return Response(
                {
                    "detail": "You do not have permission to access this dashboard."
                },
                status=403
            )

        # =========================
        # Student Profile
        # =========================

        try:
            student = Student.objects.select_related(
                "user"
            ).get(
                user=request.user
            )

        except Student.DoesNotExist:
            return Response(
                {
                    "detail": "Student profile not found."
                },
                status=404
            )

        # =========================
        # Active Enrollment
        # =========================

        enrollment = (
            Enrollment.objects
            .select_related(
                "academic_session",
                "class_name",
                "section",
            )
            .filter(
                student=student,
                status="ACTIVE"
            )
            .first()
        )

        # If no active enrollment
        if not enrollment:
            return Response({

                "student": {
                    "id": student.id,
                    "student_id": student.student_id,
                    "name": (
                        f"{student.user.first_name} "
                        f"{student.user.last_name}"
                    ).strip(),
                },

                "message": "No active enrollment found.",

                "statistics": {
                    "subjects": 0,
                    "attendance_percentage": 0,
                    "average_marks": 0,
                    "fee_due": 0,
                },

                "attendance": {
                    "present": 0,
                    "absent": 0,
                    "late": 0,
                    "excused": 0,
                },

                "today_routine": [],
                "upcoming_exams": [],
                "recent_results": [],
                "fees": {
                    "total": 0,
                    "paid": 0,
                    "due": 0,
                },
                "recent_notices": [],

            })

        # =========================
        # Student Basic Information
        # =========================

        student_data = {
            "id": student.id,
            "student_id": student.student_id,
            "name": (
                f"{student.user.first_name} "
                f"{student.user.last_name}"
            ).strip(),
            "class_name": enrollment.class_name.name,
            "section": enrollment.section.name,
            "academic_session": enrollment.academic_session.name,
        }

        # =========================
        # Teaching Assignments
        # =========================

        assignments = TeachingAssignment.objects.filter(
            class_name=enrollment.class_name,
            section=enrollment.section,
            academic_session=enrollment.academic_session,
        ).select_related(
            "subject",
            "teacher",
            "teacher__user",
        )

        total_subjects = assignments.values(
            "subject"
        ).distinct().count()

        # =========================
        # Attendance
        # =========================

        attendance_qs = Attendance.objects.filter(
            student=student,
            enrollment=enrollment,
        )

        present = attendance_qs.filter(
            status="PRESENT"
        ).count()

        absent = attendance_qs.filter(
            status="ABSENT"
        ).count()

        late = attendance_qs.filter(
            status="LATE"
        ).count()

        excused = attendance_qs.filter(
            status="EXCUSED"
        ).count()

        total_attendance = (
            present +
            absent +
            late +
            excused
        )

        attendance_percentage = (
            (present / total_attendance) * 100
            if total_attendance > 0
            else 0
        )

        # =========================
        # Today's Attendance
        # =========================

        today_attendance = attendance_qs.filter(
            date=date.today()
        )

        # =========================
        # Today's Routine
        # =========================

        day_name = date.today().strftime("%A").upper()

        today_routine = Routine.objects.filter(
            teaching_assignment__in=assignments,
            day=day_name,
        ).select_related(
            "teaching_assignment__subject",
            "teaching_assignment__teacher",
            "teaching_assignment__teacher__user",
        ).order_by(
            "start_time"
        )

        # =========================
        # Upcoming Exams
        # =========================

        upcoming_exams = Exam.objects.filter(
            class_name=enrollment.class_name,
            academic_session=enrollment.academic_session,
            start_date__gte=date.today(),
        ).order_by(
            "start_date"
        )[:5]

        # =========================
        # Results
        # =========================

        results = Result.objects.filter(
            student=student,
            exam_subject__exam__academic_session=(
                enrollment.academic_session
            ),
        ).select_related(
            "exam_subject__subject",
            "exam_subject__exam",
        ).order_by(
            "-created_at"
        )[:5]

        average_marks = Result.objects.filter(
            student=student,
            exam_subject__exam__academic_session=(
                enrollment.academic_session
            ),
        ).aggregate(
            average=Avg("marks_obtained")
        )["average"] or 0

        # =========================
        # Fees
        # =========================

        fee_qs = StudentFee.objects.filter(
            student=student
        )

        total_fee = fee_qs.aggregate(
            total=Sum("amount")
        )["total"] or 0

        total_paid = fee_qs.aggregate(
            total=Sum("paid_amount")
        )["total"] or 0

        total_due = fee_qs.aggregate(
            total=Sum("due_amount")
        )["total"] or 0

        # =========================
        # Recent Notices
        # =========================

        recent_notices = Notice.objects.filter(
            is_active=True,
            target_audience__in=[
                "ALL",
                "STUDENT",
            ],
        ).order_by(
            "-publish_date"
        )[:5]

        # =========================
        # Response
        # =========================

        return Response({

            "student": student_data,

            "statistics": {
                "subjects": total_subjects,
                "attendance_percentage": round(
                    attendance_percentage,
                    2
                ),
                "average_marks": round(
                    float(average_marks),
                    2
                ),
                "fee_due": total_due,
            },

            "attendance": {
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
            },

            "today_attendance": [
                {
                    "subject": item.teaching_assignment.subject.name,
                    "status": item.status,
                    "remarks": item.remarks,
                }
                for item in today_attendance.select_related(
                    "teaching_assignment__subject"
                )
            ],

            "today_routine": [
                {
                    "subject": (
                        routine.teaching_assignment
                        .subject.name
                    ),
                    "subject_code": (
                        routine.teaching_assignment
                        .subject.code
                    ),
                    "teacher": (
                        routine.teaching_assignment
                        .teacher.user.first_name
                    ),
                    "start_time": routine.start_time,
                    "end_time": routine.end_time,
                    "room_number": routine.room_number,
                }
                for routine in today_routine
            ],

            "upcoming_exams": [
                {
                    "id": exam.id,
                    "name": exam.name,
                    "exam_type": exam.exam_type,
                    "start_date": exam.start_date,
                    "end_date": exam.end_date,
                }
                for exam in upcoming_exams
            ],

            "recent_results": [
                {
                    "id": result.id,
                    "exam": result.exam_subject.exam.name,
                    "subject": (
                        result.exam_subject
                        .subject.name
                    ),
                    "marks": result.marks_obtained,
                    "grade": result.grade,
                    "grade_point": result.grade_point,
                    "remarks": result.remarks,
                }
                for result in results
            ],

            "fees": {
                "total": total_fee,
                "paid": total_paid,
                "due": total_due,
            },

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