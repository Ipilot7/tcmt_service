from rest_framework import serializers
from .models import Region, Hospital, HospitalMaintenance
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']
class HospitalSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'lat', 'long', 'region']
class HospitalMaintenanceSerializer(serializers.ModelSerializer):
    hospital = HospitalSerializer(read_only=True)
    class Meta:
        model = HospitalMaintenance
        fields = ['id', 'hospital', 'maintenance_date']