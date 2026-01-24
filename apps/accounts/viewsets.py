from rest_framework import viewsets
from .models import User, Role, Permission
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.prefetch_related('users').all()
    serializer_class = RoleSerializer

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.prefetch_related('roles__users').all()
    serializer_class = PermissionSerializer
