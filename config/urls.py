from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.dashboard.urls')),
    path('auth/', include('apps.users.urls')),
    path('requests/', include('apps.requests.urls', namespace='requests')),
    path('trips/', include('apps.trips.urls', namespace='trips')),
    path('i18n/', include('django.conf.urls.i18n')),
    # We will add other apps here later
]