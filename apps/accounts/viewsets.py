from rest_framework import viewsets
from .models import User, Role, Permission
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer

from .permissions import IsAdminOrManager

class UserViewSet(viewsets.ModelViewSet): # Изменили на ModelViewSet
    queryset = User.objects.prefetch_related('roles').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]

class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.prefetch_related('users').all()
    serializer_class = RoleSerializer

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.prefetch_related('roles__users').all()
    serializer_class = PermissionSerializer
