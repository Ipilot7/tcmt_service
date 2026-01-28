from django_filters import rest_framework as filters
from .models import Task

class TaskFilter(filters.FilterSet):
    task_date = filters.DateFromToRangeFilter()
    created_at = filters.DateFromToRangeFilter()
    task_number = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Task
        fields = {
            'hospital': ['exact'],
            'device_type': ['exact'],
            'status': ['exact'],
            'responsible_person': ['exact'],
        }
