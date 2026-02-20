from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from ninja.errors import HttpError

from modules.trips.models import Trip

from ..models import Booking


def create_booking_service(user, payload):
    trip = get_object_or_404(Trip, pk=payload.trip_id, status="scheduled")

    if trip.available_seats_remaining < payload.selected_seats:
        raise HttpError(400, f"Only {trip.available_seats_remaining} seats left")

    booking = Booking.objects.create(
        trip=trip,
        user=user,
        selected_seats=payload.selected_seats,
        booking_status="pending",
    )

    return booking


def get_my_bookings_service(user):
    return Booking.objects.filter(user=user).order_by("-booked_at")


def get_booking_service(user, booking_id):
    return get_object_or_404(Booking, pk=booking_id, user=user)


def cancel_booking_service(user, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, user=user)

    if booking.booking_status == "cancelled":
        raise HttpError(400, "Booking is already cancelled")

    if booking.booking_status not in ("pending", "confirmed"):
        raise HttpError(
            400, f"Cannot cancel a booking with status '{booking.booking_status}'"
        )

    booking.booking_status = "cancelled"
    booking.cancelled_at = now()
    booking.save(update_fields=["booking_status", "cancelled_at"])

    return booking
