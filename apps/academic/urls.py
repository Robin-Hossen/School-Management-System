from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import AcademicSessionViewSet, ClassViewSet, SectionViewSet, SubjectViewSet,EnrollmentViewSet, TeachingAssignmentViewSet,StudentMyClassesView

router = DefaultRouter()
router.register(r'academic-sessions', AcademicSessionViewSet, basename='academic-session')
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'sections', SectionViewSet, basename='section')
router.register(r'teaching-assignments', TeachingAssignmentViewSet, basename='teaching-assignment')
urlpatterns = router.urls + [
    path(
        'my-classes/',
        StudentMyClassesView.as_view(),
        name='student-my-classes'
    ),
]

