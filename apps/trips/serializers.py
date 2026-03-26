from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Trip, TripResult
from apps.locations.serializers import HospitalSerializer
from apps.devices.serializers import DeviceTypeSerializer
from apps.accounts.serializers import UserSerializer

class TripSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Trip
        fields = [
            'id', 'hospital', 'device_type', 'task_number', 'description', 
            'contact_phone', 'trip_date', 'order_number', 'status', 
            'status_display', 'responsible_persons', 'created_at'
        ]
        read_only_fields = ['task_number', 'created_at']

    @extend_schema_field(HospitalSerializer)
    def get_hospital(self, obj):
        return HospitalSerializer(obj.hospital).data if obj.hospital else None

    @extend_schema_field(DeviceTypeSerializer)
    def get_device_type(self, obj):
        return DeviceTypeSerializer(obj.device_type).data if obj.device_type else None

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_responsible_persons(self, obj):
        return [
            {'id': user.id, 'fullname': user.fullname} 
            for user in obj.responsible_persons.all()
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['hospital'] = self.get_hospital(instance)
        representation['device_type'] = self.get_device_type(instance)
        representation['responsible_persons'] = self.get_responsible_persons(instance)
        representation.pop('responsible_person', None)
        return representation

class TripResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripResult
        fields = ['trip', 'result_info']