from rest_framework.permissions import BasePermission
from .models import UserRole


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.TEACHER
        )


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.STUDENT
        )


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.PARENT
        )


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ACCOUNTANT
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return request.user.role == UserRole.ADMIN


class AttendancePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.role in (
                UserRole.ADMIN,
                UserRole.TEACHER,
                UserRole.STUDENT,
            )

        return request.user.role in (
            UserRole.ADMIN,
            UserRole.TEACHER,
        )

class ExamPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Everyone allowed to read
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.role in (
                UserRole.ADMIN,
                UserRole.TEACHER,
                UserRole.STUDENT,
            )

        # Only Admin can create/update/delete exams
        return request.user.role == UserRole.ADMIN


class ResultPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Everyone can read results
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.role in (
                UserRole.ADMIN,
                UserRole.TEACHER,
                UserRole.STUDENT,
            )

        # Admin and Teacher can create/update/delete
        return request.user.role in (
            UserRole.ADMIN,
            UserRole.TEACHER,
        )    



class FeeStructurePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Everyone can view fee structures
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.role in (
                UserRole.ADMIN,
                UserRole.ACCOUNTANT,
                UserRole.STUDENT,
            )

        # Only Admin and Accountant can modify
        return request.user.role in (
            UserRole.ADMIN,
            UserRole.ACCOUNTANT,
        )


class StudentFeePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Admin, Accountant and Student can view
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.role in (
                UserRole.ADMIN,
                UserRole.ACCOUNTANT,
                UserRole.STUDENT,
            )

        # Only Admin and Accountant can modify
        return request.user.role in (
            UserRole.ADMIN,
            UserRole.ACCOUNTANT,
        )


class PaymentPermission(BasePermission):
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        # =========================
        # Read Payments
        # =========================

        if request.method in ("GET", "HEAD", "OPTIONS"):

            return request.user.role in (
                UserRole.ADMIN,
                UserRole.ACCOUNTANT,
                UserRole.STUDENT,
            )

        # =========================
        # Online Checkout
        # Student can initiate
        # =========================

        if getattr(view, "action", None) == "create_checkout":

            return request.user.role in (
                UserRole.ADMIN,
                UserRole.ACCOUNTANT,
                UserRole.STUDENT,
            )

        # =========================
        # Manual Payment
        # Only Admin / Accountant
        # =========================

        return request.user.role in (
            UserRole.ADMIN,
            UserRole.ACCOUNTANT,
        )   


class NoticePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Everyone can read notices
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.role in (
                UserRole.ADMIN,
                UserRole.TEACHER,
                UserRole.STUDENT,
                UserRole.ACCOUNTANT,
            )

        # Only Admin can create/update/delete
        return request.user.role == UserRole.ADMIN    




class MessagePermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        # View messages
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # Send message
        if request.method == "POST":
            return True

        # Delete message
        if request.method == "DELETE":
            return True

        # No edit
        if request.method in ("PUT", "PATCH"):
            return False

        return False

    def has_object_permission(self, request, view, obj):

        # Sender or receiver can view
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return (
                obj.sender == request.user
                or obj.receiver == request.user
            )

        # Sender or receiver can delete
        if request.method == "DELETE":
            return (
                obj.sender == request.user
                or obj.receiver == request.user
            )

        # No edit
        return False

   




class RoutinePermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Admin, Teacher and Student can view
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return request.user.role in (
                UserRole.ADMIN,
                UserRole.TEACHER,
                UserRole.STUDENT,
            )

        # Only Admin can create/update/delete
        return request.user.role == UserRole.ADMIN