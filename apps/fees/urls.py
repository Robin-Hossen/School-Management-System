from rest_framework.routers import DefaultRouter
from .views import FeeStructureViewSet, PaymentViewSet, StudentFeeViewSet

router = DefaultRouter()

router.register(
    "fee-structures",
    FeeStructureViewSet,
    basename="fee-structure"
)
router.register(
    "student-fees",
    StudentFeeViewSet,
    basename="student-fee"
)
router.register(
    "payments",
    PaymentViewSet,
    basename="payment"
)

urlpatterns = router.urls