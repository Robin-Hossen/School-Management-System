from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from apps.accounts.models import UserRole
from apps.accounts.permissions import MessagePermission

from .filters import MessageFilter
from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [MessagePermission]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    filterset_class = MessageFilter

    search_fields = [
        "subject",
        "content",
    ]

    ordering_fields = [
        "created_at",
        "updated_at",
        "subject",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):

        if getattr(self, "swagger_fake_view", False):
            return Message.objects.none()

        user = self.request.user

        return Message.objects.filter(
            sender=user
        ) | Message.objects.filter(
            receiver=user
        )

    def perform_create(self, serializer):
        serializer.save(
            sender=self.request.user
        )