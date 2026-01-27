from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
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
    
    # API endpoints from apps (flat structure)
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.core.urls')),
    path('api/', include('apps.devices.urls')),
    path('api/', include('apps.locations.urls')),
    path('api/', include('apps.tasks.urls')),
    path('api/', include('apps.trips.urls')),

    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Root redirects for backward compatibility
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair_root'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_root'),

    # Swagger Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema')),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)