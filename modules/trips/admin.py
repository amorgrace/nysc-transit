from django.contrib import admin

from .models import Trip, Vehicle, VehicleType


@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_default", "description")
    list_filter = ("is_default",)
    search_fields = ("name",)


admin.site.register(Trip)
admin.site.register(Vehicle)
