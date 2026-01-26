from rest_framework import viewsets, filters
from .models import DeviceType, Device
from .serializers import DeviceTypeSerializer, DeviceSerializer

class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('device_type', 'hospital').all()
    serializer_class = DeviceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['serial_number', 'device_type__name', 'hospital__name']
