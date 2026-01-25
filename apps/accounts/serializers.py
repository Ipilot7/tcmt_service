from rest_framework import serializers
from .models import User, Role, Permission

class UserSerializer(serializers.ModelSerializer):
    # Поле для принятия ID ролей при создании/обновлении
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Role.objects.all(), source='roles'
    )
    
    class Meta:
        model = User
        fields = ['id', 'fullname', 'psn', 'login', 'password', 'role_ids', 'roles']
        extra_kwargs = {
            'password': {'write_only': True}, # Пароль нельзя прочитать через API
            'roles': {'read_only': True}      # Детальную инфо о ролях только читаем
        }

    def create(self, validated_data):
        # Извлекаем роли, так как create_user не ожидает их в аргументах
        roles = validated_data.pop('roles', [])
        # Создаем пользователя через менеджер для хеширования пароля
        user = User.objects.create_user(**validated_data)
        # Устанавливаем связи ManyToMany
        user.roles.set(roles)
        return user


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
