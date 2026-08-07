from rest_framework.permissions import BasePermission
from .models import UserRole

class IsAdmin(BasePermission):
    def has_permission(self,request,view):
        return (request.user and request.user.is_authenticated and request.user.role==UserRole.ADMIN)


class IsTeacher(BasePermission):
    def has_permission(self,request,view):
        return (request.user and request.user.is_authenticated and request.user.role==UserRole.TEACHER)

class IsStudent(BasePermission):
    def has_permission(self,request,view):
        return(request.user and request.user.is_authenticated and request.user.role==UserRole.STUDENT)

class IsParent(BasePermission):
    def has_permission(self,request,view):
        return(request.user and request.user.isauthenticated and request.user.role==UserRole.PARENT)

class IsAccountant(BasePermission):
    def has_permission(self,request,view):
        return(request.user and request.user.isauthenticated and request.user.role==UserRole.ACCOUNTANT)
                    