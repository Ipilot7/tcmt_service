from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'statuses', viewsets.StatusViewSet, basename='status')

urlpatterns = [
    path('', include(router.urls)),
]
