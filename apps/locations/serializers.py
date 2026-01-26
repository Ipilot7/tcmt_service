from rest_framework import serializers
from .models import Region, Hospital, HospitalMaintenance
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name']
class HospitalSerializer(serializers.ModelSerializer):
    region_info = RegionSerializer(source='region', read_only=True)
    class Meta:
        model = Hospital
        fields = ['id', 'name', 'lat', 'long', 'region', 'region_info']
class HospitalMaintenanceSerializer(serializers.ModelSerializer):
    hospital_info = HospitalSerializer(source='hospital', read_only=True)
    class Meta:
        model = HospitalMaintenance
        fields = ['id', 'hospital', 'hospital_info', 'maintenance_date']