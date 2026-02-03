from django_filters import rest_framework as filters
from .models import Hospital

class HospitalFilter(filters.FilterSet):
    class Meta:
        model = Hospital
        fields = {
            'region': ['exact'],
        }
