from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'hospital', 'device_type', 'status', 'responsible_person', 'task_date', 'created_at')
    list_filter = ('status', 'hospital', 'device_type', 'responsible_person', 'task_date', 'created_at')
    search_fields = ('task_number', 'description')
