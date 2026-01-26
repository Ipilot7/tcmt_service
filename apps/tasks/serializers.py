from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Task
from apps.locations.serializers import HospitalSerializer
from apps.devices.serializers import DeviceTypeSerializer

class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'hospital', 'device_type', 'task_number', 
            'description', 'status', 'status_display', 
            'responsible_person', 'created_at'
        ]
        read_only_fields = ['task_number', 'created_at']

    @extend_schema_field(HospitalSerializer)
    def get_hospital(self, obj):
        return HospitalSerializer(obj.hospital).data

    @extend_schema_field(DeviceTypeSerializer)
    def get_device_type(self, obj):
        return DeviceTypeSerializer(obj.device_type).data

    @extend_schema_field(serializers.DictField())
    def get_responsible_person(self, obj):
        if obj.responsible_person:
            return {
                'id': obj.responsible_person.id,
                'fullname': obj.responsible_person.fullname
            }
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['hospital'] = self.get_hospital(instance)
        representation['device_type'] = self.get_device_type(instance)
        representation['responsible_person'] = self.get_responsible_person(instance)
        return representation