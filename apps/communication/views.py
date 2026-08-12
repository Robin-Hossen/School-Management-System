from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

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

        return (
            Message.objects.filter(sender=user)
            | Message.objects.filter(receiver=user)
        )

    def perform_create(self, serializer):

        serializer.save(
            sender=self.request.user
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="read"
    )
    def mark_as_read(self, request, pk=None):

        message = self.get_object()

        if message.receiver != request.user:
            return Response(
                {
                    "detail": (
                        "Only the receiver can "
                        "mark this message as read."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        message.is_read = True

        message.save(
            update_fields=["is_read"]
        )

        return Response(
            {
                "message": "Message marked as read.",
                "is_read": message.is_read,
            },
            status=status.HTTP_200_OK
        )