from datetime import datetime
from rest_framework import viewsets, filters, serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from apps.core.choices import StatusChoices
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
        responses={201: inline_serializer(name='TripImportResponse', fields={'count': serializers.IntegerField()})}
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

@extend_schema(tags=['Trips'])
class TripAnalyticsView(APIView):
    """
    Эндпоинт для получения аналитики по поездкам (статистика по статусам и по месяцам).
    """
    @extend_schema(
        responses={
            200: inline_serializer(
                name='TripAnalyticsResponse',
                fields={
                    'total': serializers.IntegerField(),
                    'breakdown': serializers.ListField(
                        child=inline_serializer(
                            name='TripStatusBreakdown',
                            fields={
                                'id': serializers.CharField(),
                                'label': serializers.CharField(),
                                'count': serializers.IntegerField(),
                                'color': serializers.CharField(),
                            }
                        )
                    ),
                    'yearly_report': serializers.ListField(
                        child=inline_serializer(
                            name='TripYearlyReport',
                            fields={
                                'month': serializers.CharField(),
                                'count': serializers.IntegerField(),
                            }
                        )
                    )
                }
            )
        }
    )
    def get(self, request):
        # Агрегация данных по статусам
        counts = Trip.objects.values('status').annotate(count=Count('id'))
        counts_dict = {item['status']: item['count'] for item in counts}
        
        total = sum(counts_dict.values())
        
        # Соответствие цветов для фронтенда 
        colors = {
            StatusChoices.NEW: "#6366f1",      # Indigo/Blue
            StatusChoices.PENDING: "#f59e0b",  # Amber/Orange (In Progress)
            StatusChoices.COMPLETED: "#10b981",# Emerald/Green
            StatusChoices.CANCELED: "#ef4444", # Red
            StatusChoices.ON_HOLD: "#64748b",   # Slate/Grey
        }

        breakdown = []
        for code, label in StatusChoices.choices:
            breakdown.append({
                'id': code,
                'label': label,
                'count': counts_dict.get(code, 0),
                'color': colors.get(code, "#000000")
            })

        # Yearly report (last 12 months)
        from django.utils import timezone
        import datetime
        
        now = timezone.now().date()
        year = now.year
        month = now.month
        
        months_list = []
        for i in range(12):
            months_list.append(f"{year}-{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        months_list.reverse()
        
        # Start date is the first day of the oldest month in our list
        oldest_month_str = months_list[0]
        start_year, start_month = map(int, oldest_month_str.split('-'))
        start_date = datetime.date(start_year, start_month, 1)
        
        yearly_counts = Trip.objects.filter(
            created_at__gte=start_date
        ).annotate(
            month_trunc=TruncMonth('created_at')
        ).values('month_trunc').annotate(count=Count('id')).order_by('month_trunc')
        
        yearly_counts_dict = {
            item['month_trunc'].strftime('%Y-%m'): item['count'] 
            for item in yearly_counts if item['month_trunc']
        }
        
        yearly_report = []
        for month_str in months_list:
            yearly_report.append({
                'month': month_str,
                'count': yearly_counts_dict.get(month_str, 0)
            })

        return Response({
            'total': total,
            'breakdown': breakdown,
            'yearly_report': yearly_report
        })
