from datetime import datetime
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from rest_framework import serializers
from apps.core.excel_service import export_to_excel, parse_excel_file
from .models import Trip, TripResult
from .serializers import TripSerializer, TripResultSerializer
from .filters import TripFilter

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.select_related('hospital', 'device_type', 'responsible_person').all()
    serializer_class = TripSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TripFilter
    search_fields = ['task_number', 'description', 'contact_phone', 'order_number', 'hospital__name']

    @extend_schema(
        responses={200: OpenApiParameter(name='file', type=bytes, location='query', description='Excel file')}
    )
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        columns = [
            ('ID', 'id'),
            ('Номер задания', 'task_number'),
            ('Больница', 'hospital.name'),
            ('Тип оборудования', 'device_type.name'),
            ('Описание', 'description'),
            ('Телефон', 'contact_phone'),
            ('Дата поездки', 'trip_date'),
            ('Номер заказа', 'order_number'),
            ('Статус', 'status'),
            ('Ответственный', 'responsible_person.fullname'),
            ('Дата создания', 'created_at'),
        ]
        return export_to_excel(queryset, columns, "trips")

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

class TripResultViewSet(viewsets.ModelViewSet):
    queryset = TripResult.objects.select_related('trip').all()
    serializer_class = TripResultSerializer
