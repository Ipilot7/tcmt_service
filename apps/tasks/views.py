from rest_framework import viewsets
from .models import Task, TaskStatus, TaskResponsible
from .serializers import TaskSerializer, TaskStatusSerializer, TaskResponsibleSerializer
class TaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Task.objects.select_related('hospital', 'device_type').all()
    serializer_class = TaskSerializer
class TaskStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskStatus.objects.select_related('task', 'status').all()
    serializer_class = TaskStatusSerializer
class TaskResponsibleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TaskResponsible.objects.select_related('task', 'user').all()
    serializer_class = TaskResponsibleSerializer