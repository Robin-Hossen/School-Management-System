from rest_framework import viewsets
from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer

    def get_queryset(self):
        queryset = Message.objects.all()

        receiver = self.request.query_params.get("receiver")
        sender = self.request.query_params.get("sender")
        is_read = self.request.query_params.get("is_read")

        if receiver:
            queryset = queryset.filter(receiver_id=receiver)

        if sender:
            queryset = queryset.filter(sender_id=sender)

        if is_read is not None:
            queryset = queryset.filter(
                is_read=is_read.lower() == "true"
            )

        return queryset