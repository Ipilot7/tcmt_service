from rest_framework import serializers
from .models import Trip, TripStatus, TripResult, TripUser
class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['id', 'hospital', 'device_type', 'task_number', 'description', 'contact_phone', 'created_at']
class TripStatusSerializer(serializers.ModelSerializer):
    status = serializers.StringRelatedField()
    class Meta:
        model = TripStatus
        fields = ['id', 'trip', 'status', 'changed_at']
class TripResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripResult
        fields = ['trip', 'result_info']
class TripUserSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = TripUser
        fields = ['id', 'trip', 'user']