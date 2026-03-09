from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from modules.payments.models import Payment


@receiver(signal=post_save, sender=Payment)
def update_booking_balance(sender, instance, created, **kwargs):
    if not created:
        return

    booking = instance.booking
    booking.amount_paid += instance.amount

    booking.balance_due = max(
        booking.total_price - booking.amount_paid, Decimal("0.00")
    )

    if booking.balance_due == Decimal("0.00"):
        booking.payment_status = "paid"

    booking.save(update_fields=["amount_paid", "balance_due", "payment_status"])
