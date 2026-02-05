from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .models import User, Role, Permission, FCMToken
from .serializers import UserSerializer, RoleSerializer, PermissionSerializer, CustomTokenObtainPairSerializer, FCMTokenSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

from .permissions import IsAdminOrManager
from apps.core.pagination import StandardResultsSetPagination

@extend_schema(tags=['Accounts'])
class UserViewSet(viewsets.ModelViewSet): # Изменили на ModelViewSet
    queryset = User.objects.prefetch_related('roles').all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminOrManager]
    filter_backends = [filters.SearchFilter]
    search_fields = ['fullname', 'login', 'psn']
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = User.objects.prefetch_related('roles').get(pk=request.user.pk)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def register_fcm_token(self, request):
        serializer = FCMTokenSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Accounts'])
class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Role.objects.prefetch_related('users').all()
    serializer_class = RoleSerializer

@extend_schema(tags=['Accounts'])
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
