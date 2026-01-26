from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('hospital', 'device_type', 'responsible_person').all()
    serializer_class = TaskSerializer
