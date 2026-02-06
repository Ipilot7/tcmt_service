from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'trips', viewsets.TripViewSet)
router.register(r'trip-results', viewsets.TripResultViewSet)

urlpatterns = [
    path('trips/analytics/', viewsets.TripAnalyticsView.as_view(), name='trip-analytics'),
    path('', include(router.urls)),
]
