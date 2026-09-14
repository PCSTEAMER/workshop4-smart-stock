from django.contrib import admin
from .models import ServiceJob

@admin.register(ServiceJob)
class ServiceJobAdmin(admin.ModelAdmin):
    list_display = ('title', 'customer_name', 'technician', 'status', 'created_at')
    list_filter = ('status', 'technician')
    search_fields = ('title', 'customer_name', 'customer_phone')