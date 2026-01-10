from django.contrib import admin
from .models import *


@admin.register(CorperProfile)
class CorperProfileAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'state_code', 'call_up_number']  # if you have good __str__ on CorperProfile

    # Or directly:
    list_display = ['get_email', 'get_full_name', 'state_code']

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def get_full_name(self, obj):
        return obj.user.full_name
    get_full_name.short_description = "Full Name"