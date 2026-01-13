# bookings/models.py
from django.db import models
from django.conf import settings
from vendor.models import Trip, Vehicle
import uuid


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )

    trip = models.ForeignKey(
        Trip,
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.PROTECT,
        related_name='bookings',
        null=True,
        blank=True,
        help_text="Assigned vehicle (can be set later)"
    )

    seat_number = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Assigned seat number if applicable"
    )

    booking_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    payment_reference = models.CharField(
        max_length=100,
        blank=True
    )

    booked_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-booked_at']
        indexes = [
            models.Index(fields=['user', 'trip']),
            models.Index(fields=['booking_status', 'payment_status']),
            models.Index(fields=['trip', 'booking_status']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['trip', 'seat_number'],
                condition=models.Q(seat_number__isnull=False),
                name='unique_seat_per_trip'
            )
        ]

    def __str__(self):
        return f"{self.user.full_name} → {self.trip} ({self.booking_status})"

    def save(self, *args, **kwargs):
        if self.amount_paid == 0 and self.trip:
            self.amount_paid = self.trip.price_per_seat
        super().save(*args, **kwargs)