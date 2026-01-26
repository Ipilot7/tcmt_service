from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Добавляем документацию для JWT эндпоинтов
TokenObtainPairView = extend_schema_view(
    post=extend_schema(tags=['auth'], summary="Получение токена (Login)")
)(TokenObtainPairView)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints from apps
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/core/', include('apps.core.urls')),
    path('api/devices/', include('apps.devices.urls')),
    path('api/locations/', include('apps.locations.urls')),
    path('api/tasks/', include('apps.tasks.urls')),
    path('api/trips/', include('apps.trips.urls')),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Root redirects or common paths (optional)
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair_root'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_root'),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]