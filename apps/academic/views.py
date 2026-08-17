from django.shortcuts import render
from rest_framework import viewsets
from .models import AcademicSession,Class, Section,Subject,Enrollment,TeachingAssignment
from .serializers import AcademicSessionSerializer,ClassSerializer, EnrollmentSerializer,SubjectSerializer,SectionSerializer,TeachingAssignmentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Enrollment
from .serializers import StudentClassSerializer
# Create your views here.
class AcademicSessionViewSet(viewsets.ModelViewSet):
    queryset=AcademicSession.objects.all()
    serializer_class=AcademicSessionSerializer


class ClassViewSet(viewsets.ModelViewSet):
    queryset=Class.objects.all()
    serializer_class=ClassSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset=Subject.objects.all()
    serializer_class=SubjectSerializer    

class SectionViewSet(viewsets.ModelViewSet):
    queryset=Section.objects.all()
    serializer_class=SectionSerializer  

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset=Enrollment.objects.all()
    serializer_class=EnrollmentSerializer      

class TeachingAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = TeachingAssignmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        queryset = TeachingAssignment.objects.select_related(
            "teacher__user",
            "teacher",
            "subject",
            "class_name",
            "section",
            "academic_session",
        )

        # Teacher হলে শুধু নিজের assignment দেখাবে
        try:
            teacher = user.teacher
            return queryset.filter(
                teacher=teacher
            )

        except Exception:
            # Admin/other user হলে সব assignment
            return queryset





# Class ar subject and class dekhanor jonne


class StudentMyClassesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "STUDENT":
            return Response(
                {
                    "detail": "Only students can access this page."
                },
                status=403
            )

        try:

            student = request.user.student_profile

        except Exception:

            return Response(
                {
                    "detail": "Student profile not found."
                },
                status=404
            )


        enrollments = Enrollment.objects.filter(
            student=student,
            status="ACTIVE"
        ).select_related(
            "academic_session",
            "class_name",
            "section"
        )


        serializer = StudentClassSerializer(
            enrollments,
            many=True
        )


        return Response(
            {
                "student": {
                    "id": student.id,
                    "student_id": student.student_id,
                    "name": (
                        f"{student.user.first_name} "
                        f"{student.user.last_name}"
                    ).strip(),
                },
                "classes": serializer.data
            }
        )