from django.shortcuts import render
from rest_framework import viewsets
from .models import AcademicSession,Class, Section,Subject,Enrollment
from .serializers import AcademicSessionSerializer,ClassSerializer, EnrollmentSerializer,SubjectSerializer,SectionSerializer


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