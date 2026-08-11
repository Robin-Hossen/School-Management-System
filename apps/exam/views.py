from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
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

from .filters import (
    ExamFilter,
    ExamSubjectFilter,
    ResultFilter,
)

from .models import Exam, ExamSubject, Result

from .serializers import (
    ExamSerializer,
    ExamSubjectSerializer,
    ResultSerializer,
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

    ordering = ["-start_date"]


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


# =========================================================
# Result ViewSet
# =========================================================

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
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

from .filters import (
    ExamFilter,
    ExamSubjectFilter,
    ResultFilter,
)

from .models import Exam, ExamSubject, Result

from .serializers import (
    ExamSerializer,
    ExamSubjectSerializer,
    ResultSerializer,
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

    ordering = ["-start_date"]


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

    ordering = ["-marks_obtained"]

    # =====================================================
    # Queryset
    # =====================================================

    def get_queryset(self):

        # Prevent swagger/schema error
        if getattr(
            self,
            "swagger_fake_view",
            False
        ):
            return Result.objects.none()

        queryset = Result.objects.select_related(
            "student__user",
            "exam_subject__exam",
            "exam_subject__subject",
        )

        user = self.request.user

        # -------------------------
        # Admin
        # -------------------------

        if user.role == UserRole.ADMIN:
            return queryset

        # -------------------------
        # Teacher
        # -------------------------

        if user.role == UserRole.TEACHER:
            return queryset

        # -------------------------
        # Student
        # -------------------------

        if user.role == UserRole.STUDENT:
            return queryset.filter(
                student__user=user
            )

        return Result.objects.none()

    # =====================================================
    # Student GPA
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
                description="Exam ID (optional)",
            ),
        ]
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="student-gpa",
    )
    def student_gpa(self, request):

        # =================================================
        # Get parameters
        # =================================================

        student_id = request.query_params.get(
            "student"
        )

        exam_id = request.query_params.get(
            "exam"
        )

        # =================================================
        # Validate student
        # =================================================

        if not student_id:

            return Response(
                {
                    "detail": "student is required."
                },
                status=400,
            )

        # =================================================
        # Base queryset
        # =================================================

        queryset = Result.objects.filter(
            student_id=student_id
        ).select_related(
            "student__user",
            "exam_subject__exam",
            "exam_subject__subject",
        )

        # =================================================
        # Filter by exam
        # =================================================

        if exam_id:

            queryset = queryset.filter(
                exam_subject__exam_id=exam_id
            )

        # =================================================
        # Check result exists
        # =================================================

        if not queryset.exists():

            return Response(
                {
                    "detail": "No results found."
                },
                status=404,
            )

        # =================================================
        # Student
        # =================================================

        first_result = queryset.first()

        student = first_result.student

        # =================================================
        # Exam
        # =================================================

        exam = first_result.exam_subject.exam

        # =================================================
        # Calculate
        # =================================================

        total_subjects = queryset.count()

        total_marks = sum(
            float(result.marks_obtained)
            for result in queryset
        )

        total_grade_points = sum(
            float(result.grade_point)
            for result in queryset
        )

        average_marks = (
            total_marks / total_subjects
        )

        gpa = (
            total_grade_points / total_subjects
        )

        # =================================================
        # Response
        # =================================================

        return Response(
            {
                "student": student.id,

                "student_code": student.student_id,

                "student_name": (
                    f"{student.user.first_name} "
                    f"{student.user.last_name}"
                ).strip(),

                "exam": exam.id,

                "exam_name": exam.name,

                "total_subjects": total_subjects,

                "total_marks": round(
                    total_marks,
                    2,
                ),

                "average_marks": round(
                    average_marks,
                    2,
                ),

                "gpa": round(
                    gpa,
                    2,
                ),
            }
        )