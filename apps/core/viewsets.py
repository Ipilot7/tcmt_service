from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from .choices import StatusChoices

class StatusViewSet(viewsets.ViewSet):
    """
    ViewSet to list available status choices.
    """
    @extend_schema(
        responses={
            200: inline_serializer(
                name='StatusListResponse',
                fields={
                    'id': serializers.CharField(),
                    'name': serializers.CharField(),
                },
                many=True
            )
        }
    )
    def list(self, request):
        data = [
            {'id': choice[0], 'name': choice[1]}
            for choice in StatusChoices.choices
        ]
        return Response(data)
