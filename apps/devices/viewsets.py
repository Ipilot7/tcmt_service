from rest_framework import viewsets, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, inline_serializer
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from apps.core.pagination import StandardResultsSetPagination
from apps.locations.models import Region
from .models import DeviceType, Device
from .serializers import DeviceTypeSerializer, DeviceSerializer
from .filters import DeviceFilter

from rest_framework.parsers import MultiPartParser, FormParser

@extend_schema(tags=['Devices'])
class DeviceTypeViewSet(viewsets.ModelViewSet):
    queryset = DeviceType.objects.all()
    serializer_class = DeviceTypeSerializer
    parser_classes = [MultiPartParser, FormParser]

@extend_schema(tags=['Devices'])
class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related('device_type', 'hospital', 'hospital__region').all()
    serializer_class = DeviceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = DeviceFilter
    search_fields = ['serial_number', 'device_type__name', 'hospital__name']

    @action(detail=False, methods=['get'])
    def by_regions(self, request):
        """
        Returns device counts grouped by regions.
        """
        regions = Region.objects.annotate(
            device_count=Count('hospitals__devices')
        ).order_by('-device_count')
        
        data = [
            {
                'id': region.id,
                'name': region.name,
                'count': region.device_count
            }
            for region in regions
        ]
        return Response(data)

@extend_schema(tags=['Devices'])
class DeviceAnalyticsView(APIView):
    """
    Endpoint for device analytics (statistics by regions).
    """
    @extend_schema(
        responses={
            200: inline_serializer(
                name='DeviceAnalyticsResponse',
                fields={
                    'total': serializers.IntegerField(),
                    'by_region': serializers.ListField(
                        child=inline_serializer(
                            name='DeviceRegionStat',
                            fields={
                                'id': serializers.IntegerField(),
                                'label': serializers.CharField(),
                                'count': serializers.IntegerField(),
                                'color': serializers.CharField(),
                            }
                        )
                    )
                }
            )
        }
    )
    def get(self, request):
        total = Device.objects.count()
        
        region_stats = Region.objects.annotate(
            count=Count('hospitals__devices')
        ).filter(count__gt=0).order_by('-count')
        
        preset_colors = [
            "#6366f1", "#f59e0b", "#10b981", "#ef4444", "#64748b",
            "#8b5cf6", "#ec4899", "#06b6d4", "#f97316", "#84cc16",
        ]

        by_region = []
        for i, region in enumerate(region_stats):
            by_region.append({
                'id': region.id,
                'label': region.name,
                'count': region.count,
                'color': preset_colors[i % len(preset_colors)]
            })

        return Response({
            'total': total,
            'by_region': by_region
        })
