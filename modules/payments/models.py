import random
import string
from uuid import uuid4

from django.conf import settings
from django.db import models

from modules.bookings.models import Booking


class Payment(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    )

    PAYMENT_METHOD_CHOICES = (
        ("card", "Card"),
        ("bank_transfer", "Bank Transfer"),
        ("paypal", "PayPal"),
        ("wallet", "Wallet"),
    )

    id = models.BigAutoField(primary_key=True, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments"
    )

    booking = models.ForeignKey(
        Booking, on_delete=models.PROTECT, related_name="payments"
    )

    payment_reference = models.CharField(max_length=20, unique=True, editable=False)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=50, choices=PAYMENT_METHOD_CHOICES, default="card"
    )

    payment_gateway = models.CharField(max_length=50, blank=True, null=True)

    gateway_response = models.JSONField(blank=True, null=True, default=dict)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    paid_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "booking"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.payment_reference} ({self.status})"

    def generate_payment_reference(self) -> str:
        """Generates a short unique payment reference like A-9F3B21C4D"""
        letter = random.choice(string.ascii_uppercase)
        return f"{letter}-{uuid4().hex[:10].upper()}"

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            self.payment_reference = self.generate_payment_reference()

        super().save(*args, **kwargs)
