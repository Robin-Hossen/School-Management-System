from rest_framework.routers import DefaultRouter
from .views import AcademicSessionViewSet, ClassViewSet, SectionViewSet, SubjectViewSet,EnrollmentViewSet

router = DefaultRouter()
router.register(r'academic-sessions', AcademicSessionViewSet, basename='academic-session')
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'sections', SectionViewSet, basename='section')
urlpatterns = router.urls

