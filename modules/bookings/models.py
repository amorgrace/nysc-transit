# bookings/models.py
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

from modules.trips.models import Trip, Vehicle


class Booking(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("no_show", "No Show"),
    )

    PAYMENT_STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name="bookings")

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name="bookings",
        null=True,
        blank=True,
        help_text="Assigned vehicle (can be set later)",
    )

    seat_number = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Assigned seat number if applicable"
    )

    selected_seats = models.PositiveSmallIntegerField(
        default=1, help_text="Number of seats selected"
    )

    booking_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_reference = models.CharField(max_length=100, blank=True)

    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        db_table = "bookings"
        ordering = ["-booked_at"]
        indexes = [
            models.Index(fields=["user", "trip"]),
            models.Index(fields=["booking_status", "payment_status"]),
            models.Index(fields=["trip", "booking_status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["trip", "seat_number"],
                condition=models.Q(seat_number__isnull=False),
                name="unique_seat_per_trip",
            )
        ]

    def __str__(self):
        return f"{self.user.full_name} → {self.trip} ({self.booking_status})"

    def save(self, *args, **kwargs):
        if self.trip and (self.amount_paid is None or self.amount_paid == 0):
            self.amount_paid = self.total_price
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        """
        Calculate total price after early bird and group discounts.
        """
        if not self.trip:
            return Decimal(0)

        base_amount = self.selected_seats * self.trip.price_per_seat
        discount = Decimal(0)

        if (
            self.trip.early_bird_discount_percentage > 0
            and not self.trip.early_bird_deadline_expired
        ):
            discount += base_amount * self.trip.early_bird_discount_rate

        if self.selected_seats > 1 and self.trip.group_discount_percentage > 0:
            discount += base_amount * self.trip.group_discount_rate

        total = base_amount - discount
        return max(total, Decimal(0))
