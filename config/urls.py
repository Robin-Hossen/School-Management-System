from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
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
    #Token Authentication
    path(
    "api/v1/auth/token/",
    TokenObtainPairView.as_view(),
    name="token_obtain_pair",
    ),

    path(
    "api/v1/auth/token/refresh/",
    TokenRefreshView.as_view(),
    name="token_refresh",
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
    path(
    "api/v1/",
    include("apps.notice.urls")
    ),
    path(
    "api/v1/",
    include("apps.communication.urls")
    ),
    path(
        "api/v1/dashboard/", 
        include("apps.dashboard.urls")
        ),

    path(
    "api/v1/accounts/",
    include("apps.accounts.urls")
    ),  
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)