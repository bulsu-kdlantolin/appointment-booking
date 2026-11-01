from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'service', 'scheduled_for')
    list_filter = ('service',)
    search_fields = ('client_name', 'email')
