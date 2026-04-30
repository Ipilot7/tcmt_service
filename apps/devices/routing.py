from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/devices/(?P<serial_number>[a-zA-Z0-9_-]+)/status/$', consumers.DeviceConsumer.as_asgi()),
]
