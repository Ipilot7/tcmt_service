from django.db.models import Count
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
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
