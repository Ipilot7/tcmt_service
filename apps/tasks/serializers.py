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
            'responsible_persons', 'task_date', 'created_at'
        ]
        read_only_fields = ['task_number', 'created_at']

    @extend_schema_field(HospitalSerializer)
    def get_hospital(self, obj):
        return HospitalSerializer(obj.hospital).data

    @extend_schema_field(DeviceTypeSerializer)
    def get_device_type(self, obj):
        return DeviceTypeSerializer(obj.device_type).data

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
        # Для обратной совместимости или если клиент ждет старое имя (но лучше приучать к новому)
        representation.pop('responsible_person', None) 
        return representation