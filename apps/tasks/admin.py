from django.contrib import admin
from .models import Task, TaskStatus, TaskResponsible

class TaskStatusInline(admin.TabularInline):
    model = TaskStatus
    extra = 1

class TaskResponsibleInline(admin.TabularInline):
    model = TaskResponsible
    extra = 1

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'hospital', 'device_type', 'created_at')
    list_filter = ('hospital', 'device_type', 'created_at')
    search_fields = ('task_number', 'description')
    inlines = [TaskStatusInline, TaskResponsibleInline]

@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ('task', 'status', 'changed_at')
    list_filter = ('status', 'changed_at')

@admin.register(TaskResponsible)
class TaskResponsibleAdmin(admin.ModelAdmin):
    list_display = ('task', 'user')
    list_filter = ('user',)
