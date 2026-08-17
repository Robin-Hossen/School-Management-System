from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, serializers, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from apps.accounts.models import UserRole
from apps.accounts.permissions import (
    ExamPermission,
    ResultPermission,
)

from apps.academic.models import Enrollment

from .filters import (
    ExamFilter,
    ExamSubjectFilter,
    ResultFilter,
)

from .models import (
    Exam,
    ExamSubject,
    Result,
)

from .serializers import (
    ExamSerializer,
    ExamSubjectSerializer,
    ResultSerializer,
    EnterResultsSerializer,
)


# =========================================================
# Exam ViewSet
# =========================================================

class ExamViewSet(viewsets.ModelViewSet):

    queryset = Exam.objects.all()

    serializer_class = ExamSerializer

    permission_classes = [ExamPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ExamFilter

    search_fields = [
        "name",
        "exam_type",
    ]

    ordering_fields = [
        "name",
        "exam_type",
        "start_date",
        "end_date",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-start_date",
    ]


# =========================================================
# Exam Subject ViewSet
# =========================================================

class ExamSubjectViewSet(viewsets.ModelViewSet):

    queryset = ExamSubject.objects.all()

    serializer_class = ExamSubjectSerializer

    permission_classes = [ExamPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ExamSubjectFilter

    search_fields = [
        "exam__name",
        "subject__name",
    ]

    ordering_fields = [
        "exam_date",
        "start_time",
        "end_time",
        "total_marks",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "exam_date",
        "start_time",
    ]


    @action(
    detail=False,
    methods=["get"],
    url_path="my-exams"
    )
    def my_exams(self, request):

        exam_subjects = (
            ExamSubject.objects
            .filter(
                teaching_assignment__teacher__user=request.user
        )
        .select_related(
            "exam",
            "exam__academic_session",
            "exam__class_name",
            "subject",
            "teaching_assignment",
            "teaching_assignment__teacher",
            "teaching_assignment__class_name",
            "teaching_assignment__section",
            "teaching_assignment__academic_session",
        )
        .order_by(
            "exam_date",
            "start_time"
        )
        )

        serializer = self.get_serializer(
            exam_subjects,
            many=True
        )

        return Response(serializer.data)


# =========================================================
# Result ViewSet
# =========================================================

class ResultViewSet(viewsets.ModelViewSet):

    serializer_class = ResultSerializer

    permission_classes = [ResultPermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = ResultFilter

    search_fields = [
        "student__student_id",
        "student__user__first_name",
        "student__user__last_name",
        "exam_subject__exam__name",
        "exam_subject__subject__name",
        "grade",
        "remarks",
    ]

    ordering_fields = [
        "marks_obtained",
        "grade",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-marks_obtained",
    ]

    # =====================================================
    # QUERYSET
    # =====================================================

    def get_queryset(self):

        # Swagger protection
        if getattr(
            self,
            "swagger_fake_view",
            False
        ):
            return Result.objects.none()

        queryset = (
            Result.objects
            .select_related(
                "student__user",

                "exam_subject__exam",
                "exam_subject__subject",

                "exam_subject__teaching_assignment",
                "exam_subject__teaching_assignment__teacher__user",
                "exam_subject__teaching_assignment__class_name",
                "exam_subject__teaching_assignment__section",
                "exam_subject__teaching_assignment__academic_session",
            )
        )

        user = self.request.user

        # =================================================
        # ADMIN
        # =================================================

        if user.role == UserRole.ADMIN:
            return queryset

        # =================================================
        # TEACHER
        # =================================================

        if user.role == UserRole.TEACHER:

            return queryset.filter(
                exam_subject__teaching_assignment__teacher__user=user
            ).distinct()

        # =================================================
        # STUDENT
        # =================================================

        if user.role == UserRole.STUDENT:

            return queryset.filter(
                student__user=user
            )

        # =================================================
        # OTHER USERS
        # =================================================

        return Result.objects.none()

    # =====================================================
    # CLASS STUDENTS
    # =====================================================

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="exam_subject",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Exam Subject ID",
            )
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="class-students",
    )
    def class_students(self, request):

        # =================================================
        # Only Teacher
        # =================================================

        if request.user.role != UserRole.TEACHER:

            return Response(
                {
                    "detail":
                        "Only teachers can access class students."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # =================================================
        # Get Exam Subject ID
        # =================================================

        exam_subject_id = request.query_params.get(
            "exam_subject"
        )

        if not exam_subject_id:

            return Response(
                {
                    "detail":
                        "exam_subject is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Get Exam Subject
        # =================================================

        try:

            exam_subject = (
                ExamSubject.objects
                .select_related(
                    "exam",
                    "subject",
                    "exam__class_name",
                    "exam__academic_session",

                    "teaching_assignment",
                    "teaching_assignment__teacher",
                    "teaching_assignment__teacher__user",
                    "teaching_assignment__class_name",
                    "teaching_assignment__section",
                    "teaching_assignment__academic_session",
                )
                .get(
                    id=exam_subject_id
                )
            )

        except ExamSubject.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Exam subject not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =================================================
        # Teaching Assignment
        # =================================================

        assignment = exam_subject.teaching_assignment

        if not assignment:

            return Response(
                {
                    "detail":
                        "No teaching assignment is linked "
                        "to this exam subject."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Teacher Ownership
        # =================================================

        if assignment.teacher.user != request.user:

            return Response(
                {
                    "detail":
                        "You are not assigned to this subject."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # =================================================
        # Active Students
        # =================================================

        enrollments = (
            Enrollment.objects
            .filter(
                academic_session=assignment.academic_session,
                class_name=assignment.class_name,
                section=assignment.section,
                status=Enrollment.Status.ACTIVE,
            )
            .select_related(
                "student__user"
            )
        )

        # =================================================
        # Existing Results
        # =================================================

        existing_results = {
            result.student_id: result
            for result in Result.objects.filter(
                exam_subject=exam_subject
            )
        }

        # =================================================
        # Response
        # =================================================

        data = []

        for enrollment in enrollments:

            student = enrollment.student

            result = existing_results.get(
                student.id
            )

            data.append(
                {
                    "student_id":
                        student.id,

                    "student_code":
                        student.student_id,

                    "student_name":
                        (
                            f"{student.user.first_name} "
                            f"{student.user.last_name}"
                        ).strip(),

                    "exam_subject":
                        exam_subject.id,

                    "exam_name":
                        exam_subject.exam.name,

                    "subject_name":
                        exam_subject.subject.name,

                    "total_marks":
                        exam_subject.total_marks,

                    "result_id":
                        result.id
                        if result
                        else None,

                    "marks_obtained":
                        float(result.marks_obtained)
                        if result
                        else None,

                    "grade":
                        result.grade
                        if result
                        else None,

                    "grade_point":
                        float(result.grade_point)
                        if result
                        else None,

                    "remarks":
                        result.remarks
                        if result
                        else "",
                }
            )

        return Response(data)

    # =====================================================
    # ENTER / UPDATE RESULTS
    # =====================================================

    @extend_schema(
        request=EnterResultsSerializer,
        responses=ResultSerializer(many=True),
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="enter-results",
    )
    def enter_results(self, request):

        # =================================================
        # Permission
        # =================================================

        if request.user.role not in (
            UserRole.ADMIN,
            UserRole.TEACHER,
        ):

            return Response(
                {
                    "detail":
                        "Only teachers and admins can enter results."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # =================================================
        # Request Data
        # =================================================

        exam_subject_id = request.data.get(
            "exam_subject"
        )

        results = request.data.get(
            "results"
        )

        # =================================================
        # Validation
        # =================================================

        if not exam_subject_id:

            return Response(
                {
                    "detail":
                        "exam_subject is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(results, list):

            return Response(
                {
                    "detail":
                        "results must be a list."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not results:

            return Response(
                {
                    "detail":
                        "results must not be empty."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Get Exam Subject
        # =================================================

        try:

            exam_subject = (
                ExamSubject.objects
                .select_related(
                    "exam",
                    "subject",

                    "teaching_assignment",
                    "teaching_assignment__teacher",
                    "teaching_assignment__teacher__user",
                    "teaching_assignment__class_name",
                    "teaching_assignment__section",
                    "teaching_assignment__academic_session",
                )
                .get(
                    id=exam_subject_id
                )
            )

        except ExamSubject.DoesNotExist:

            return Response(
                {
                    "detail":
                        "Exam subject not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =================================================
        # Teaching Assignment
        # =================================================

        assignment = exam_subject.teaching_assignment

        if not assignment:

            return Response(
                {
                    "detail":
                        "No teaching assignment is linked "
                        "to this exam subject."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Teacher Ownership
        # =================================================

        if request.user.role == UserRole.TEACHER:

            if assignment.teacher.user != request.user:

                return Response(
                    {
                        "detail":
                            "You are not assigned to this subject."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # =================================================
        # Total Marks
        # =================================================

        total_marks = exam_subject.total_marks

        saved_results = []

        # =================================================
        # Transaction
        # =================================================

        try:

            with transaction.atomic():

                for item in results:

                    student_id = item.get(
                        "student"
                    )

                    marks_obtained = item.get(
                        "marks_obtained"
                    )

                    remarks = item.get(
                        "remarks",
                        ""
                    )

                    # =====================================
                    # Student Required
                    # =====================================

                    if not student_id:

                        raise serializers.ValidationError(
                            {
                                "detail":
                                    "student is required."
                            }
                        )

                    # =====================================
                    # Marks Required
                    # =====================================

                    if marks_obtained is None:

                        raise serializers.ValidationError(
                            {
                                "detail":
                                    f"Marks are required "
                                    f"for student {student_id}."
                            }
                        )

                    # =====================================
                    # Marks Validation
                    # =====================================

                    try:

                        marks = float(
                            marks_obtained
                        )

                    except (
                        TypeError,
                        ValueError,
                    ):

                        raise serializers.ValidationError(
                            {
                                "detail":
                                    f"Invalid marks "
                                    f"for student {student_id}."
                            }
                        )

                    # =====================================
                    # Marks Range
                    # =====================================

                    if (
                        marks < 0
                        or marks > total_marks
                    ):

                        raise serializers.ValidationError(
                            {
                                "detail":
                                    f"Marks for student "
                                    f"{student_id} must be "
                                    f"between 0 and "
                                    f"{total_marks}."
                            }
                        )

                    # =====================================
                    # Enrollment Validation
                    # =====================================

                    is_valid_student = (
                        Enrollment.objects
                        .filter(
                            student_id=student_id,

                            academic_session=(
                                assignment.academic_session
                            ),

                            class_name=(
                                assignment.class_name
                            ),

                            section=(
                                assignment.section
                            ),

                            status=(
                                Enrollment.Status.ACTIVE
                            ),
                        )
                        .exists()
                    )

                    if not is_valid_student:

                        raise serializers.ValidationError(
                            {
                                "detail":
                                    f"Student {student_id} "
                                    "is not enrolled in the "
                                    "assigned class/section."
                            }
                        )

                    # =====================================
                    # Create / Update
                    # =====================================

                    result, created = (
                        Result.objects
                        .update_or_create(
                            student_id=student_id,

                            exam_subject=(
                                exam_subject
                            ),

                            defaults={
                                "marks_obtained":
                                    marks_obtained,

                                "remarks":
                                    remarks,
                            },
                        )
                    )

                    # =====================================
                    # Serialize
                    # =====================================

                    saved_results.append(
                        ResultSerializer(
                            result,
                            context={
                                "request": request
                            }
                        ).data
                    )

        except serializers.ValidationError as error:

            return Response(
                error.detail,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Response
        # =================================================

        return Response(
            {
                "message":
                    "Results saved successfully.",

                "exam_subject":
                    exam_subject.id,

                "exam_name":
                    exam_subject.exam.name,

                "subject_name":
                    exam_subject.subject.name,

                "total_marks":
                    total_marks,

                "results":
                    saved_results,
            },
            status=status.HTTP_200_OK,
        )

    # =====================================================
    # STUDENT GPA
    # =====================================================

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="student",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Student ID",
            ),

            OpenApiParameter(
                name="exam",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Exam ID. If omitted, all exams are considered."
                ),
            ),
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="student-gpa",
    )
    def student_gpa(self, request):

        student_id = request.query_params.get(
            "student"
        )

        exam_id = request.query_params.get(
            "exam"
        )

        # =================================================
        # Student Required
        # =================================================

        if not student_id:

            return Response(
                {
                    "detail":
                        "student is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Student Security
        # =================================================

        if request.user.role == UserRole.STUDENT:

            try:
                own_student = request.user.student_profile

            except Exception:

                return Response(
                    {
                        "detail":
                            "Student profile not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if int(student_id) != own_student.id:

                return Response(
                    {
                        "detail":
                            "You can only view your own result."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # =================================================
        # Query
        # =================================================

        queryset = (
            Result.objects
            .filter(
                student_id=student_id
            )
            .select_related(
                "student__user",
                "exam_subject__exam",
                "exam_subject__subject",
            )
        )

        # =================================================
        # Exam Filter
        # =================================================

        if exam_id:

            queryset = queryset.filter(
                exam_subject__exam_id=exam_id
            )

        # =================================================
        # No Result
        # =================================================

        if not queryset.exists():

            return Response(
                {
                    "detail":
                        "No results found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =================================================
        # Student
        # =================================================

        first_result = queryset.first()

        student = first_result.student

        # =================================================
        # Calculate
        # =================================================

        total_subjects = queryset.count()

        total_marks = sum(
            float(
                result.marks_obtained
            )
            for result in queryset
        )

        total_grade_points = sum(
            float(
                result.grade_point
            )
            for result in queryset
        )

        average_marks = (
            total_marks /
            total_subjects
        )

        gpa = (
            total_grade_points /
            total_subjects
        )

        # =================================================
        # Exam
        # =================================================

        if exam_id:

            exam = first_result.exam_subject.exam

            exam_response = exam.id

            exam_name_response = exam.name

        else:

            exam_response = None

            exam_name_response = "All Exams"

        # =================================================
        # Response
        # =================================================

        return Response(
            {
                "student":
                    student.id,

                "student_code":
                    student.student_id,

                "student_name":
                    (
                        f"{student.user.first_name} "
                        f"{student.user.last_name}"
                    ).strip(),

                "exam":
                    exam_response,

                "exam_name":
                    exam_name_response,

                "total_subjects":
                    total_subjects,

                "total_marks":
                    round(
                        total_marks,
                        2,
                    ),

                "average_marks":
                    round(
                        average_marks,
                        2,
                    ),

                "gpa":
                    round(
                        gpa,
                        2,
                    ),
            }
        )

    # =====================================================
    # EXAM-WISE STUDENT RESULT
    # =====================================================

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="student",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Student ID",
            ),

            OpenApiParameter(
                name="exam",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=True,
                description="Exam ID",
            ),
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="exam-result",
    )
    def exam_result(self, request):

        student_id = request.query_params.get(
            "student"
        )

        exam_id = request.query_params.get(
            "exam"
        )

        # =================================================
        # Validation
        # =================================================

        if not student_id:

            return Response(
                {
                    "detail":
                        "student is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not exam_id:

            return Response(
                {
                    "detail":
                        "exam is required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # =================================================
        # Student Security
        # =================================================

        if request.user.role == UserRole.STUDENT:

            try:
                own_student = request.user.student_profile

            except Exception:

                return Response(
                    {
                        "detail":
                            "Student profile not found."
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if int(student_id) != own_student.id:

                return Response(
                    {
                        "detail":
                            "You can only view your own result."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        # =================================================
        # Get Results
        # =================================================

        queryset = (
            Result.objects
            .filter(
                student_id=student_id,
                exam_subject__exam_id=exam_id,
            )
            .select_related(
                "student__user",
                "exam_subject__exam",
                "exam_subject__subject",
            )
            .order_by(
                "exam_subject__subject__name"
            )
        )

        # =================================================
        # No Result
        # =================================================

        if not queryset.exists():

            return Response(
                {
                    "detail":
                        "No results found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =================================================
        # Student / Exam
        # =================================================

        first_result = queryset.first()

        student = first_result.student

        exam = first_result.exam_subject.exam

        # =================================================
        # Subjects
        # =================================================

        subjects = []

        total_marks_obtained = 0

        total_possible_marks = 0

        total_grade_points = 0

        for result in queryset:

            marks = float(
                result.marks_obtained
            )

            subject_total_marks = (
                result.exam_subject.total_marks
            )

            grade_point = float(
                result.grade_point
            )

            total_marks_obtained += marks

            total_possible_marks += (
                subject_total_marks
            )

            total_grade_points += (
                grade_point
            )

            subjects.append(
                {
                    "result_id":
                        result.id,

                    "subject_id":
                        result.exam_subject.subject.id,

                    "subject_name":
                        result.exam_subject.subject.name,

                    "marks_obtained":
                        marks,

                    "total_marks":
                        subject_total_marks,

                    "grade":
                        result.grade,

                    "grade_point":
                        grade_point,

                    "remarks":
                        result.remarks,
                }
            )

        # =================================================
        # Summary
        # =================================================

        total_subjects = queryset.count()

        average_marks = (
            total_marks_obtained /
            total_subjects
        )

        gpa = (
            total_grade_points /
            total_subjects
        )

        # =================================================
        # Response
        # =================================================

        return Response(
            {
                "student": {
                    "id":
                        student.id,

                    "code":
                        student.student_id,

                    "name":
                        (
                            f"{student.user.first_name} "
                            f"{student.user.last_name}"
                        ).strip(),
                },

                "exam": {
                    "id":
                        exam.id,

                    "name":
                        exam.name,
                },

                "subjects":
                    subjects,

                "summary": {
                    "total_subjects":
                        total_subjects,

                    "total_marks":
                        round(
                            total_marks_obtained,
                            2,
                        ),

                    "total_possible_marks":
                        total_possible_marks,

                    "average_marks":
                        round(
                            average_marks,
                            2,
                        ),

                    "gpa":
                        round(
                            gpa,
                            2,
                        ),
                },
            }
        )

    # =====================================================
    # MY RESULT
    # =====================================================

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="exam",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                required=False,
                description="Exam ID (optional)",
            )
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="my-result",
    )
    def my_result(self, request):

        # =================================================
        # Only Student
        # =================================================

        if request.user.role != UserRole.STUDENT:

            return Response(
                {
                    "detail":
                        "Only students can access this endpoint."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # =================================================
        # Student Profile
        # =================================================

        try:

            student = request.user.student_profile

        except Exception:

            return Response(
                {
                    "detail":
                        "Student profile not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =================================================
        # Exam
        # =================================================

        exam_id = request.query_params.get(
            "exam"
        )

        # =================================================
        # Query
        # =================================================

        queryset = (
            Result.objects
            .filter(
                student=student
            )
            .select_related(
                "student__user",
                "exam_subject__exam",
                "exam_subject__subject",
            )
            .order_by(
                "exam_subject__subject__name"
            )
        )

        # =================================================
        # Exam Filter
        # =================================================

        if exam_id:

            queryset = queryset.filter(
                exam_subject__exam_id=exam_id
            )

        # =================================================
        # No Results
        # =================================================

        if not queryset.exists():

            return Response(
                {
                    "detail":
                        "No results found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # =================================================
        # Student / Exam
        # =================================================

        first_result = queryset.first()

        exam = first_result.exam_subject.exam

        # =================================================
        # Subjects
        # =================================================

        subjects = []

        total_marks_obtained = 0

        total_possible_marks = 0

        total_grade_points = 0

        for result in queryset:

            marks = float(
                result.marks_obtained
            )

            subject_total_marks = (
                result.exam_subject.total_marks
            )

            grade_point = float(
                result.grade_point
            )

            total_marks_obtained += marks

            total_possible_marks += (
                subject_total_marks
            )

            total_grade_points += (
                grade_point
            )

            subjects.append(
                {
                    "result_id":
                        result.id,

                    "subject_id":
                        result.exam_subject.subject.id,

                    "subject_name":
                        result.exam_subject.subject.name,

                    "marks_obtained":
                        marks,

                    "total_marks":
                        subject_total_marks,

                    "grade":
                        result.grade,

                    "grade_point":
                        grade_point,

                    "remarks":
                        result.remarks,
                }
            )

        # =================================================
        # Summary
        # =================================================

        total_subjects = queryset.count()

        average_marks = (
            total_marks_obtained /
            total_subjects
        )

        gpa = (
            total_grade_points /
            total_subjects
        )

        # =================================================
        # Response
        # =================================================

        return Response(
            {
                "student": {
                    "id":
                        student.id,

                    "code":
                        student.student_id,

                    "name":
                        (
                            f"{student.user.first_name} "
                            f"{student.user.last_name}"
                        ).strip(),
                },

                "exam": {
                    "id":
                        exam.id,

                    "name":
                        exam.name,
                },

                "subjects":
                    subjects,

                "summary": {
                    "total_subjects":
                        total_subjects,

                    "total_marks":
                        round(
                            total_marks_obtained,
                            2,
                        ),

                    "total_possible_marks":
                        total_possible_marks,

                    "average_marks":
                        round(
                            average_marks,
                            2,
                        ),

                    "gpa":
                        round(
                            gpa,
                            2,
                        ),
                },
            }
        )