from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'regions', viewsets.RegionViewSet)
router.register(r'hospitals', viewsets.HospitalViewSet)
router.register(r'hospital-maintenances', viewsets.HospitalMaintenanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
