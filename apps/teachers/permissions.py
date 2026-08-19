from rest_framework.permissions import BasePermission
from apps.accounts.models import UserRole


class TeacherPermission(BasePermission):

    def has_permission(self, request, view):

        # Home page থেকে teacher list দেখা যাবে
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # Teacher create/update/delete শুধু Admin
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )