from rest_framework import serializers
from .models import DeviceType, Device
from apps.locations.serializers import HospitalSerializer

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ['id', 'name']

class DeviceSerializer(serializers.ModelSerializer):
    device_type_info = DeviceTypeSerializer(source='device_type', read_only=True)
    hospital_info = HospitalSerializer(source='hospital', read_only=True)
    
    class Meta:
        model = Device
        fields = ['id', 'serial_number', 'hospital', 'hospital_info', 'device_type', 'device_type_info']