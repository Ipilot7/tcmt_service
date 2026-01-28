from django.urls import path, include
from rest_framework import routers
from . import viewsets
from .views_autoupdate import AppcastView

router = routers.DefaultRouter()
router.register(r'statuses', viewsets.StatusViewSet, basename='status')

urlpatterns = [
    path('', include(router.urls)),
    path('autoupdate/win/', AppcastView.as_view(), name='autoupdate-win'),
]
