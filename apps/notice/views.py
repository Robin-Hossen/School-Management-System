from rest_framework import viewsets
from .models import Notice
from .serializers import NoticeSerializer
from apps.accounts.permissions import IsAdmin,IsAdminOrReadOnly



class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all()
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminOrReadOnly]  # Only admin users can create, update, or delete notices; others can only read.
