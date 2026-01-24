from rest_framework import viewsets
from .models import Task, TaskStatus, TaskResponsible
from .serializers import TaskSerializer, TaskStatusSerializer, TaskResponsibleSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('hospital', 'device_type').all()
    serializer_class = TaskSerializer

class TaskStatusViewSet(viewsets.ModelViewSet):
    queryset = TaskStatus.objects.select_related('task', 'status').all()
    serializer_class = TaskStatusSerializer

class TaskResponsibleViewSet(viewsets.ModelViewSet):
    queryset = TaskResponsible.objects.select_related('task', 'user').all()
    serializer_class = TaskResponsibleSerializer
