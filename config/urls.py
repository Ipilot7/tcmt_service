from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.utils import extend_schema_view, extend_schema

# Import viewsets
from apps.accounts import viewsets as accounts_viewsets
from apps.core import viewsets as core_viewsets
from apps.devices import viewsets as devices_viewsets
from apps.locations import viewsets as locations_viewsets
from apps.tasks import viewsets as tasks_viewsets
from apps.trips import viewsets as trips_viewsets

router = routers.DefaultRouter()
# Register viewsets from each app
router.register(r'users', accounts_viewsets.UserViewSet)
router.register(r'roles', accounts_viewsets.RoleViewSet)
router.register(r'permissions', accounts_viewsets.PermissionViewSet)
router.register(r'statuses', core_viewsets.StatusViewSet, basename='status')
router.register(r'device-types', devices_viewsets.DeviceTypeViewSet)
router.register(r'devices', devices_viewsets.DeviceViewSet)
router.register(r'regions', locations_viewsets.RegionViewSet)
router.register(r'hospitals', locations_viewsets.HospitalViewSet)
router.register(r'hospital-maintenances', locations_viewsets.HospitalMaintenanceViewSet)
router.register(r'tasks', tasks_viewsets.TaskViewSet)
router.register(r'trips', trips_viewsets.TripViewSet)
router.register(r'trip-results', trips_viewsets.TripResultViewSet)

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
    path('api/', include(router.urls)),
    path('', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/logout/', accounts_viewsets.LogoutView.as_view(), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair_root'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_root'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
]