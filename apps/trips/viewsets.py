from datetime import datetime
from rest_framework import viewsets, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from apps.core.excel_service import export_to_excel, parse_excel_file
from apps.core.pagination import StandardResultsSetPagination
from .models import Trip, TripResult
from .serializers import TripSerializer, TripResultSerializer
from .filters import TripFilter

@extend_schema(tags=['Trips'])
class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('hospital', 'device_type', 'responsible_person').all()
    serializer_class = TripSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TripFilter
    search_fields = ['task_number', 'description', 'contact_phone', 'order_number', 'hospital__name']

    @extend_schema(
        responses={
            200: inline_serializer(
                name='TripFileUrlResponse',
                fields={'file_url': serializers.URLField()}
            ),
        },
        description="Экспорт поездок в Excel-файл. Возвращает URL-ссылку для скачивания."
    )
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        columns = [
            ('ID', 'id'),
            ('Номер задания', 'task_number'),
            ('ID Больницы', 'hospital_id'),
            ('Больница', 'hospital.name'),
            ('ID Типа оборудования', 'device_type_id'),
            ('Тип оборудования', 'device_type.name'),
            ('Описание', 'description'),
            ('Телефон', 'contact_phone'),
            ('Дата поездки', 'trip_date'),
            ('ID Ответственного', 'responsible_person_id'),
            ('Ответственный', 'responsible_person.fullname'),
            ('Номер заказа', 'order_number'),
            ('Статус', 'status'),
            ('Дата создания', 'created_at'),
        ]
        relative_path = export_to_excel(queryset, columns, "trips")
        file_url = request.build_absolute_uri(f"/media/{relative_path}")
        return JsonResponse({"file_url": file_url})

    @extend_schema(
        request={
            'multipart/form-data': inline_serializer(
                name='TripImportSerializer',
                fields={'file': serializers.FileField()}
            )
        },
        responses={201: inline_serializer(name='ImportResponse', fields={'count': serializers.IntegerField()})}
    )
    @action(detail=False, methods=['post'])
    def import_excel(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        column_map = {
            'ID Больницы': 'hospital_id',
            'ID Типа оборудования': 'device_type_id',
            'Описание': 'description',
            'Телефон': 'contact_phone',
            'Статус': 'status',
            'ID Ответственного': 'responsible_person_id',
            'Дата поездки': 'trip_date',
            'Номер заказа': 'order_number',
        }
        
        try:
            data = parse_excel_file(file, column_map)
            created_count = 0
            for item in data:
                # Basic validation for required fields
                if not item.get('hospital_id') or not item.get('device_type_id') or not item.get('description') or not item.get('contact_phone'):
                    continue
                
                # Check date format if present
                trip_date = item.get('trip_date')
                if isinstance(trip_date, str):
                    try:
                        item['trip_date'] = datetime.strptime(trip_date, '%Y-%m-%d').date()
                    except ValueError:
                        item['trip_date'] = None

                Trip.objects.create(**item)
                created_count += 1
            
            return Response({"count": created_count}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

@extend_schema(tags=['Trips'])
class TripResultViewSet(viewsets.ModelViewSet):
    queryset = TripResult.objects.select_related('trip').all()
    serializer_class = TripResultSerializer
