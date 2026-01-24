from rest_framework import serializers
from .models import DeviceType, Device

class DeviceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceType
        fields = ['id', 'name']
class DeviceSerializer(serializers.ModelSerializer):
    device_type = DeviceTypeSerializer(read_only=True)
    class Meta:
        model = Device
        fields = ['id', 'serial_number', 'hospital', 'device_type']