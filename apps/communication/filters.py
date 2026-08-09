import django_filters

from .models import Message


class MessageFilter(django_filters.FilterSet):

    class Meta:
        model = Message
        fields = [
            "sender",
            "receiver",
            "is_read",
            "created_at",
        ]