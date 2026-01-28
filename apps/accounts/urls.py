from django.urls import path, include
from rest_framework import routers
from . import viewsets

router = routers.DefaultRouter()
router.register(r'users', viewsets.UserViewSet)
router.register(r'roles', viewsets.RoleViewSet)
router.register(r'permissions', viewsets.PermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', viewsets.LogoutView.as_view(), name='logout'),
]
