from django.contrib import admin
from .models import Request

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('request_number', 'created_at', 'responsible', 'status')
    list_filter = ('status', 'region', 'created_at')
    search_fields = ('request_number', 'description')
