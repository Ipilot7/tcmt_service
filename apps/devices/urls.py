from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'device-types', viewsets.DeviceTypeViewSet)
router.register(r'devices', viewsets.DeviceViewSet)

urlpatterns = [
    path('devices/analytics/', viewsets.DeviceAnalyticsView.as_view(), name='device-analytics'),
    path('', include(router.urls)),
]
