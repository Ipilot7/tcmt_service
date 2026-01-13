from django.contrib import admin
from .models import Trip

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'created_at', 'responsible', 'status', 'escort_name')
    list_filter = ('status', 'region', 'created_at')
    search_fields = ('request_number', 'description', 'escort_name')
