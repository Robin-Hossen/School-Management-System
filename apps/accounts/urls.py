from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    ProfileView,
    AdminTestView,
    LogoutView,
    CustomTokenObtainPairView,
    ChangePasswordView,
)

urlpatterns = [
    path(
        "login/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),

    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout"
    ),

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),

    path(
        "admin-test/",
        AdminTestView.as_view(),
        name="admin-test"
    ),
    path(
    "change-password/",
    ChangePasswordView.as_view(),
    name="change-password"
),
]