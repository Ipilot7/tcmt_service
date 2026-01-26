from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'', viewsets.TaskViewSet, basename='task')

urlpatterns = [
    path('analytics/', viewsets.TaskAnalyticsView.as_view(), name='task-analytics'),
    path('', include(router.urls)),
]
