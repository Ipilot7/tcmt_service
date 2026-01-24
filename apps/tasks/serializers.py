from rest_framework import serializers
from .models import Task, TaskStatus, TaskResponsible

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'hospital', 'device_type', 'task_number', 'description', 'created_at']
class TaskStatusSerializer(serializers.ModelSerializer):
    status = serializers.StringRelatedField()
    class Meta:
        model = TaskStatus
        fields = ['id', 'task', 'status', 'changed_at']
class TaskResponsibleSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = TaskResponsible
        fields = ['id', 'task', 'user']