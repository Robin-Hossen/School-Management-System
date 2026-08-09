from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import NoticePermission

from .filters import NoticeFilter
from .models import Notice
from .serializers import NoticeSerializer


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [NoticePermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = NoticeFilter

    search_fields = [
        "title",
        "content",
    ]

    ordering_fields = [
        "title",
        "publish_date",
        "created_at",
        "updated_at",
    ]

    ordering = ["-publish_date"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Notice.objects.none()

        user = self.request.user

        # Admin sees everything
        if user.role == UserRole.ADMIN:
            return Notice.objects.all()

        # Other users only see active notices
        queryset = Notice.objects.filter(
            is_active=True
        )

        if user.role == UserRole.STUDENT:
            return queryset.filter(
                target_audience__in=["ALL", "STUDENT"]
            )

        if user.role == UserRole.TEACHER:
            return queryset.filter(
                target_audience__in=["ALL", "TEACHER"]
            )

        if user.role == UserRole.ACCOUNTANT:
            return queryset.filter(
                target_audience__in=["ALL", "STAFF"]
            )

        return Notice.objects.none()