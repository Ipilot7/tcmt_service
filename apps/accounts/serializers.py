from rest_framework import serializers
from .models import User, Role, Permission

class RoleSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    # Поле для принятия ID ролей при создании/обновлении
    role_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Role.objects.all(), source='roles', required=False
    )
    roles = RoleSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'fullname', 'psn', 'login', 'password', 'role_ids', 'roles']
        extra_kwargs = {
            'password': {'write_only': True}, # Пароль нельзя прочитать через API
        }

    def create(self, validated_data):
        # Извлекаем роли, так как create_user не ожидает их в аргументах
        roles = validated_data.pop('roles', [])
        # Создаем пользователя через менеджер для хеширования пароля
        user = User.objects.create_user(**validated_data)
        
        # Если роли не переданы, назначаем роль по умолчанию 'user'
        if not roles:
            default_role = Role.objects.filter(name='user').first()
            if default_role:
                roles = [default_role]
        
        # Устанавливаем связи ManyToMany
        if roles:
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
