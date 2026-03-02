from django.contrib import admin, messages
from .models import Trip, TripResult
from apps.core.notifications import send_push_notification

class TripResultInline(admin.StackedInline):
    model = TripResult
    can_delete = False

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('task_number', 'hospital', 'device_type', 'status', 'get_responsible_persons', 'trip_date', 'created_at')
    list_filter = ('status', 'hospital', 'device_type', 'responsible_persons', 'trip_date', 'created_at')
    search_fields = ('task_number', 'description', 'contact_phone', 'order_number')
    inlines = [TripResultInline]
    actions = ['send_notification']

    def get_responsible_persons(self, obj):
        return ", ".join([user.fullname for user in obj.responsible_persons.all()])
    get_responsible_persons.short_description = 'Responsible Persons'

    @admin.action(description="Отправить повторное уведомление всем ответственным")
    def send_notification(self, request, queryset):
        sent_count = 0
        for trip in queryset:
            for person in trip.responsible_persons.all():
                send_push_notification(
                    user=person,
                    title="Напоминание о поездке",
                    body=f"Напоминание по поездке {trip.task_number}: {trip.description[:50]}...",
                    data={"trip_id": str(trip.id), "type": "trip_reminder"}
                )
                sent_count += 1
        self.message_user(request, f"Отправлено {sent_count} уведомлений заинтересованным лицам.", messages.SUCCESS)

@admin.register(TripResult)
class TripResultAdmin(admin.ModelAdmin):
    list_display = ('trip',)
