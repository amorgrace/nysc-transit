import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    pass


class VehicleType(models.Model):
    class Meta:
        db_table = "vehicle_type"

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    STATUS_CHOICES = (
        ("active", "Active/Available"),
        ("maintenance", "In Maintenance"),
        ("inactive", "Inactive"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "vendor"},
        related_name="vehicles",
    )

    registration_number = models.CharField(
        max_length=20, unique=True, help_text="Plate number e.g. ABC-123DE"
    )

    vehicle_type = models.ForeignKey(
        "VehicleType",
        on_delete=models.SET_NULL,
        null=True,
        related_name="vehicles",
        help_text="Choose a default type or create a custom one",
    )
    make_model = models.CharField(max_length=100, help_text="e.g. Toyota Hiace 2020")
    color = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveSmallIntegerField(help_text="Total passenger seats")
    year_manufactured = models.PositiveIntegerField(blank=True, null=True)
    amenities = models.JSONField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    is_insured = models.BooleanField(default=False)
    insurance_expiry = models.DateField(null=True, blank=True)

    roadworthiness_expiry_date = models.DateField(null=True, blank=True)
    vehicle_images = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicle"
        ordering = ["-created_at"]

    def __str__(self):
        vendor_name = getattr(self.vendor, "full_name", str(self.vendor))
        return f"{self.make_model} - {self.registration_number} ({vendor_name})"

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def is_inactive(self):
        return self.status == "inactive"

    @property
    def is_under_maintenance(self):
        return self.status == "maintenance"

    @property
    def is_insurance_valid(self):
        if not self.is_insured or not self.insurance_expiry:
            return False
        return self.insurance_expiry >= timezone.now().date()

    @property
    def is_roadworthy(self):
        if not self.roadworthiness_expiry_date:
            return False
        return self.roadworthiness_expiry_date >= timezone.now().date()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Trip(models.Model):
    STATUS_CHOICES = (
        ("scheduled", "Scheduled"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    )

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={"role": "vendor"},
        related_name="trips",
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,  # don't allow vehicle deletion if trip exists
        related_name="trips",
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    description = models.TextField(blank=True)

    departure_state = models.CharField(max_length=150)
    departure_city = models.CharField(
        max_length=150, help_text="Starting point e.g. Iyana-Ipaja"
    )
    destination_camp = models.CharField(
        max_length=150, help_text="Destination e.g. NYSC Camp, Iyana-Ipaja"
    )
    departure_date = models.DateField()
    departure_time = models.TimeField()
    estimated_arrival_time = models.TimeField(null=True, blank=True)

    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveSmallIntegerField(default=0)

    early_bird_discount_percentage = models.PositiveSmallIntegerField(default=0)
    early_bird_deadline = models.DateField(null=True, blank=True)
    group_discount_percentage = models.PositiveSmallIntegerField(default=0)

    refund_policy = models.TextField(blank=True)
    luggage_allowance = models.CharField(max_length=200, blank=True)
    special_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "trip"
        ordering = ["departure_date", "departure_time"]
        indexes = [
            models.Index(fields=["departure_date", "status"]),
            models.Index(fields=["vendor", "status"]),
        ]

    def __str__(self):
        return f"{self.departure_city} {self.departure_state} → {self.destination_camp} | {self.departure_date} {self.departure_time}"

    @property
    def is_scheduled(self):
        return self.status == "scheduled"

    @property
    def is_completed(self):
        return self.status == "completed"

    @property
    def is_ongoing(self):
        return self.status == "ongoing"

    @property
    def is_cancelled(self):
        return self.status == "cancelled"

    @property
    def group_discount_rate(self):
        return Decimal(self.group_discount_percentage) / Decimal(100)

    @property
    def early_bird_discount_rate(self):
        return Decimal(self.early_bird_discount_percentage) / Decimal(100)

    @property
    def early_bird_deadline_expired(self):
        if not self.early_bird_deadline:
            return False
        return self.early_bird_deadline < timezone.now().date()

    @property
    def total_seats_booked(self):
        related = getattr(self, "bookings", None)
        if related is None:
            related = getattr(self, "booking_set", None)
        if related is None:
            return 0
        return related.aggregate(total=models.Sum("selected_seats"))["total"] or 0

    @property
    def available_seats_remaining(self):
        if self.vehicle:
            return self.vehicle.capacity - self.total_seats_booked
        return 0

    def clean(self):
        if self.price_per_seat < 0:
            raise ValidationError({"price_per_seat": "Price cannot be negative."})

        remaining = self.available_seats_remaining
        if self.vehicle and remaining < 0:
            raise ValidationError(
                {"available_seats": "Selected seats exceed vehicle capacity."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
