from rest_framework.routers import DefaultRouter
from .views import ExamSubjectViewSet, ExamViewSet, ResultViewSet

router = DefaultRouter()

router.register(
    "exams",
    ExamViewSet,
    basename="exam"
)
router.register(
    "exam-subjects",
    ExamSubjectViewSet,
    basename="exam-subject"
)
router.register(
    "results",
    ResultViewSet,
    basename="result"
)

urlpatterns = router.urls