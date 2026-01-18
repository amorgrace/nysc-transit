from django.contrib import admin

from .models import Trip, Vehicle, VendorProfile


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = [
        "get_email",
        "business_name",
        "business_registration_number",
        "years_in_operation",
    ]
    search_fields = ["user__email", "business_name", "business_registration_number"]

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = "Email"


admin.site.register(Trip)
admin.site.register(Vehicle)
