from rest_framework import serializers
from .models import User, Role, Permission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fullname', 'psn']

class RoleSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    class Meta:
        model = Role
        fields = ['id', 'name', 'users']

class PermissionSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    class Meta:
        model = Permission
        fields = ['id', 'name', 'roles']
