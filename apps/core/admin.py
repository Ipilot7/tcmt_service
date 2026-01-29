from django.contrib import admin

# Legacy StatusAdmin removed as Status model is gone
from .models import AppUpdate

@admin.register(AppUpdate)
class AppUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'version', 'pub_date', 'os_type', 'length')
    list_filter = ('os_type', 'pub_date')
    search_fields = ('title', 'version', 'description')
    ordering = ('-pub_date',)
    readonly_fields = ('length',)
    fields = ('title', 'version', 'os_type', 'file', 'description', 'file_type', 'length')
