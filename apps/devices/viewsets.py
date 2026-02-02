from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.pagination import StandardResultsSetPagination
from .models import DeviceType, Device
from .serializers import DeviceTypeSerializer, DeviceSerializer
from .filters import DeviceFilter

@extend_schema(tags=['Devices'])
class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer

@extend_schema(tags=['Devices'])
class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('device_type', 'hospital').all()
    serializer_class = DeviceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DeviceFilter
    search_fields = ['serial_number', 'device_type__name', 'hospital__name']
