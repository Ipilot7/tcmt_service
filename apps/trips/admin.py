from django.contrib import admin
from .models import Trip, TripResult

class TripResultInline(admin.StackedInline):
    model = TripResult
    can_delete = False

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'hospital', 'device_type', 'status', 'responsible_person', 'trip_date', 'created_at')
    list_filter = ('status', 'hospital', 'device_type', 'responsible_person', 'trip_date', 'created_at')
    search_fields = ('task_number', 'description', 'contact_phone', 'order_number')
    inlines = [TripResultInline]

@admin.register(TripResult)
class TripResultAdmin(admin.ModelAdmin):
    list_display = ('trip',)
