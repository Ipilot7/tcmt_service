from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import DeviceType, Device
from .serializers import DeviceTypeSerializer, DeviceSerializer
from .filters import DeviceFilter

class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('device_type', 'hospital').all()
    serializer_class = DeviceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DeviceFilter
    search_fields = ['serial_number', 'device_type__name', 'hospital__name']
