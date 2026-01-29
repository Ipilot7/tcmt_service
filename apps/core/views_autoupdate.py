from rest_framework.views import APIView
from rest_framework import permissions, renderers
from django.http import HttpResponse
from django.template.loader import render_to_string
from drf_spectacular.utils import extend_schema
from .models import AppUpdate

class PlainXMLRenderer(renderers.BaseRenderer):
    media_type = 'application/xml'
    format = 'xml'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data

class AppcastView(APIView):
    """
    Эндпоинт для автообновления Windows-приложения (Appcast/Sparkle XML).
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    renderer_classes = [PlainXMLRenderer]

    def perform_content_negotiation(self, request, force=False):
        return (PlainXMLRenderer(), 'application/xml')

    @extend_schema(
        responses={(200, 'application/xml'): str},
        description="Возвращает XML для системы автообновления Sparkle."
    )
    def get(self, request, *args, **kwargs):
        # We only want the latest update for the appcast
        updates = AppUpdate.objects.filter(os_type='windows').order_by('-pub_date')[:1]
        
        xml_content = render_to_string('core/appcast.xml', {
            'object_list': updates,
            'request': request
        })
        
        return HttpResponse(xml_content, content_type='application/xml')
