from django_filters import rest_framework as filters
from .models import Trip

class TripFilter(filters.FilterSet):
    trip_date = filters.DateFromToRangeFilter()
    created_at = filters.DateFromToRangeFilter()
    task_number = filters.CharFilter(lookup_expr='icontains')
    order_number = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Trip
        fields = {
            'hospital': ['exact'],
            'device_type': ['exact'],
            'status': ['exact'],
            'responsible_person': ['exact'],
        }
