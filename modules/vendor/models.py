import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Vendor(models.Model):
    VERIFICATION_PENDING = "pending"
    VERIFICATION_UNDER_REVIEW = "under_review"
    VERIFICATION_APPROVED = "verified"
    VERIFICATION_REJECTED = "rejected"

    VERIFICATION_CHOICES = [
        (VERIFICATION_PENDING, "Pending"),
        (VERIFICATION_UNDER_REVIEW, "Under Review"),
        (VERIFICATION_APPROVED, "Verified"),
        (VERIFICATION_REJECTED, "Rejected"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
    )
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=150)
    business_registration_number = models.CharField(max_length=100, unique=True)
    years_in_operation = models.PositiveIntegerField()
    logo_url = models.URLField(blank=True, null=True)
    verification_documents = models.JSONField(blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default=VERIFICATION_PENDING,
    )
    rejection_reason = models.TextField(blank=True, null=True)
    rating_average = models.FloatField(
        default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    payout_bank_name = models.CharField(max_length=100, blank=True)
    payout_account_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendors"

    @property
    def is_verified(self):
        return self.verification_status == self.VERIFICATION_APPROVED


class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ("bus", "Bus (18-60 seater)"),
        ("minibus", "Minibus (12-15 seater)"),
        ("van", "Van (8-12 seater)"),
        ("car", "Car/SUV (4-7 seater)"),
    )

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

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    make_model = models.CharField(max_length=100, help_text="e.g. Toyota Hiace 2020")
    color = models.CharField(max_length=50, blank=True)
    capacity = models.PositiveSmallIntegerField(help_text="Total passenger seats")
    year_of_manufacture = models.PositiveIntegerField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    is_insured = models.BooleanField(default=False)
    insurance_expiry = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.make_model} - {self.registration_number} ({self.vendor.full_name})"
        )


# vendor/models.py (continue in the same file)
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

    trip_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
    )
    origin = models.CharField(
        max_length=150, help_text="Starting point e.g. Iyana-Ipaja"
    )
    destination = models.CharField(
        max_length=150, help_text="Destination e.g. NYSC Camp, Iyana-Ipaja"
    )
    departure_date = models.DateField()
    departure_time = models.TimeField()
    estimated_arrival_time = models.TimeField(null=True, blank=True)

    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    available_seats = models.PositiveSmallIntegerField(default=0)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["departure_date", "departure_time"]
        indexes = [
            models.Index(fields=["departure_date", "status"]),
            models.Index(fields=["vendor", "status"]),
        ]

    def __str__(self):
        return f"{self.origin} → {self.destination} | {self.departure_date} {self.departure_time}"
