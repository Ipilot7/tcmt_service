from rest_framework import viewsets
from .models import Region, Hospital, HospitalMaintenance
from .serializers import RegionSerializer, HospitalSerializer, HospitalMaintenanceSerializer

class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
class HospitalViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Hospital.objects.select_related('region').all()
    serializer_class = HospitalSerializer
class HospitalMaintenanceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HospitalMaintenance.objects.select_related('hospital').all()
    serializer_class = HospitalMaintenanceSerializer