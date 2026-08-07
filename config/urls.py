from django.contrib import admin
from django.urls import include, path

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path(
        'api/v1/auth/',
        include('apps.accounts.urls')
    ),

    # Swagger schema
    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema',
    ),

    # Swagger UI
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema'
        ),
        name='swagger-ui',
    ),
    path(
        'api/v1/',
        include('apps.students.urls')
    ),
    path(
    "api/v1/",
    include("apps.academic.urls")
    ),
    path(
    "api/v1/",
    include("apps.teachers.urls")
    ),
    path(
    "api/v1/",
    include("apps.routine.urls")
    ),
    path(
    "api/v1/",
    include("apps.attendance.urls")
    ),
    path(
    "api/v1/",
    include("apps.exam.urls")
    ),
    path(
    "api/v1/",
    include("apps.fees.urls")
    ),
]