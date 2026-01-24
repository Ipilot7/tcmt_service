from django.contrib import admin
from .models import Trip, TripStatus, TripResult, TripUser

class TripStatusInline(admin.TabularInline):
    model = TripStatus
    extra = 1

class TripUserInline(admin.TabularInline):
    model = TripUser
    extra = 1

class TripResultInline(admin.StackedInline):
    model = TripResult
    can_delete = False

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'hospital', 'device_type', 'contact_phone', 'created_at')
    list_filter = ('hospital', 'device_type', 'created_at')
    search_fields = ('task_number', 'description', 'contact_phone')
    inlines = [TripStatusInline, TripUserInline, TripResultInline]

@admin.register(TripStatus)
class TripStatusAdmin(admin.ModelAdmin):
    list_display = ('trip', 'status', 'changed_at')
    list_filter = ('status', 'changed_at')

@admin.register(TripResult)
class TripResultAdmin(admin.ModelAdmin):
    list_display = ('trip',)

@admin.register(TripUser)
class TripUserAdmin(admin.ModelAdmin):
    list_display = ('trip', 'user')
    list_filter = ('user',)
