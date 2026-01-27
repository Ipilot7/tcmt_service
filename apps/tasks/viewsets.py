from datetime import datetime
from django.db import models
from django.db.models import Count
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter
from rest_framework import serializers
from rest_framework.views import APIView
from apps.core.excel_service import export_to_excel, parse_excel_file
from apps.core.choices import StatusChoices
from .models import Task
from .serializers import TaskSerializer
from .filters import TaskFilter

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.select_related('hospital', 'device_type', 'responsible_person').all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = TaskFilter
    search_fields = ['task_number', 'description', 'hospital__name']

    @extend_schema(
        responses={
            200: inline_serializer(
                name='FileUrlResponse',
                fields={'file_url': serializers.URLField()}
            ),
        },
        description="Экспорт задач в Excel-файл. Возвращает URL-ссылку для скачивания."
    )
    @action(detail=False, methods=['get'])
    def export_excel(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        columns = [
            ('ID', 'id'),
            ('Номер задачи', 'task_number'),
            ('Больница', 'hospital.name'),
            ('Тип оборудования', 'device_type.name'),
            ('Описание', 'description'),
            ('Статус', 'status'),
            ('Ответственный', 'responsible_person.fullname'),
            ('Дата задачи', 'task_date'),
            ('Дата создания', 'created_at'),
        ]
        relative_path = export_to_excel(queryset, columns, "tasks")
        file_url = request.build_absolute_uri(f"/media/{relative_path}")
        return JsonResponse({"file_url": file_url})

    @extend_schema(
        request={
            'multipart/form-data': inline_serializer(
                name='TaskImportSerializer',
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
            'Статус': 'status',
            'ID Ответственного': 'responsible_person_id',
            'Дата задачи': 'task_date',
        }
        
        try:
            data = parse_excel_file(file, column_map)
            created_count = 0
            for item in data:
                # Basic validation for required fields
                if not item.get('hospital_id') or not item.get('device_type_id') or not item.get('description'):
                    continue
                
                # Check date format if present
                task_date = item.get('task_date')
                if isinstance(task_date, str):
                    try:
                        item['task_date'] = datetime.strptime(task_date, '%Y-%m-%d').date()
                    except ValueError:
                        item['task_date'] = None

                Task.objects.create(**item)
                created_count += 1
            
            return Response({"count": created_count}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class TaskAnalyticsView(APIView):
    """
    Эндпоинт для получения аналитики по задачам (статистика по статусам).
    """
    @extend_schema(
        responses={
            200: inline_serializer(
                name='TaskAnalyticsResponse',
                fields={
                    'total': serializers.IntegerField(),
                    'breakdown': serializers.ListField(
                        child=inline_serializer(
                            name='StatusBreakdown',
                            fields={
                                'id': serializers.CharField(),
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
        # Агрегация данных
        counts = Task.objects.values('status').annotate(count=Count('id'))
        counts_dict = {item['status']: item['count'] for item in counts}
        
        total = sum(counts_dict.values())
        
        # Соответствие цветов для фронтенда (как на макете)
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

        return Response({
            'total': total,
            'breakdown': breakdown
        })
