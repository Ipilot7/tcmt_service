from rest_framework import viewsets
from .models import Trip, TripStatus, TripResult, TripUser
from .serializers import TripSerializer, TripStatusSerializer, TripResultSerializer, TripUserSerializer

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('hospital', 'device_type').all()
    serializer_class = TripSerializer

class TripStatusViewSet(viewsets.ModelViewSet):
    queryset = TripStatus.objects.select_related('trip', 'status').all()
    serializer_class = TripStatusSerializer

class TripResultViewSet(viewsets.ModelViewSet):
    queryset = TripResult.objects.select_related('trip').all()
    serializer_class = TripResultSerializer

class TripUserViewSet(viewsets.ModelViewSet):
    queryset = TripUser.objects.select_related('trip', 'user').all()
    serializer_class = TripUserSerializer
