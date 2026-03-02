from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'tasks', viewsets.TaskViewSet, basename='task')
router.register(r'task-categories', viewsets.TaskCategoryViewSet, basename='taskcategory')

urlpatterns = [
    path('tasks/analytics/', viewsets.TaskAnalyticsView.as_view(), name='task-analytics'),
    path('', include(router.urls)),
]
