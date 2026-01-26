from rest_framework import viewsets, filters
from .models import Trip, TripResult
from .serializers import TripSerializer, TripResultSerializer

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('hospital', 'device_type', 'responsible_person').all()
    serializer_class = TripSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['task_number', 'description', 'contact_phone', 'order_number', 'hospital__name']

class TripResultViewSet(viewsets.ModelViewSet):
    queryset = TripResult.objects.select_related('trip').all()
    serializer_class = TripResultSerializer
