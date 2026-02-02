from rest_framework import viewsets, filters
from drf_spectacular.utils import extend_schema
from apps.core.pagination import StandardResultsSetPagination
from .models import Region, Hospital, HospitalMaintenance
from .serializers import RegionSerializer, HospitalSerializer, HospitalMaintenanceSerializer

@extend_schema(tags=['Locations'])
class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

@extend_schema(tags=['Locations'])
class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.select_related('region').all()
    serializer_class = HospitalSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'region__name']

@extend_schema(tags=['Locations'])
class HospitalMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = HospitalMaintenance.objects.select_related('hospital').all()
    serializer_class = HospitalMaintenanceSerializer
