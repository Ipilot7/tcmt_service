from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .models import User, Role, Permission
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer

from .permissions import IsAdminOrManager

class UserViewSet(viewsets.ModelViewSet): # Изменили на ModelViewSet
    queryset = User.objects.prefetch_related('roles').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrManager]
    filter_backends = [filters.SearchFilter]
    search_fields = ['fullname', 'login', 'psn']

class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.prefetch_related('users').all()
    serializer_class = RoleSerializer

class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Permission.objects.prefetch_related('roles__users').all()
    serializer_class = PermissionSerializer

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        tags=['auth'],
        request=inline_serializer(
            name='LogoutRequest',
            fields={
                'refresh': serializers.CharField(),
            }
        ),
        responses={205: None}
    )
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
