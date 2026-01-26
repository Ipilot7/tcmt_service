from rest_framework import viewsets, filters
from .models import Region, Hospital, HospitalMaintenance
from .serializers import RegionSerializer, HospitalSerializer, HospitalMaintenanceSerializer

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class HospitalViewSet(viewsets.ModelViewSet):
    queryset = Hospital.objects.select_related('region').all()
    serializer_class = HospitalSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'region__name']

class HospitalMaintenanceViewSet(viewsets.ModelViewSet):
    queryset = HospitalMaintenance.objects.select_related('hospital').all()
    serializer_class = HospitalMaintenanceSerializer
