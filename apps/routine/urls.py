from rest_framework.routers import DefaultRouter
from .views import RoutineViewSet

router = DefaultRouter()

router.register(
    "routines",
    RoutineViewSet,
    basename="routine"
)

urlpatterns = router.urls