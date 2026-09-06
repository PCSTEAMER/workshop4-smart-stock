from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'status', 'phone_number', 'approved_by', 'updated_at')
    list_filter = ('status', 'role')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone_number')