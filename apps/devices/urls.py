from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'device-types', viewsets.DeviceTypeViewSet)
router.register(r'devices', viewsets.DeviceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
