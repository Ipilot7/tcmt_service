from django_filters import rest_framework as filters
from .models import Device

class DeviceFilter(filters.FilterSet):
    serial_number = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Device
        fields = {
            'hospital': ['exact'],
            'device_type': ['exact'],
        }
