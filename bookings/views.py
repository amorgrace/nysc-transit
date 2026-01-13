from ninja import Router, Schema
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from typing import List

from django.shortcuts import get_object_or_404
from .schemas import *
from .models import Booking
from vendor.models import Trip

router = Router(tags=["Bookings"], auth=JWTAuth())

@router.post("/", response=BookingOut)
def create_booking(request, payload: BookingIn):
    trip = get_object_or_404(Trip, pk=payload.trip_id, status="scheduled")

    if trip.available_seats < payload.seats:
        raise HttpError(400, f"Only {trip.available_seats} seats left")

    total = trip.price_per_seat * payload.seats

    booking = Booking.objects.create(
        trip=trip,
        user=request.user,
        seats=payload.seats,
        total_price=total,
        status="pending",          # or "confirmed" if no payment step
    )

    # Decrease available seats
    trip.available_seats -= payload.seats
    trip.save(update_fields=["available_seats"])

    return booking


@router.get("/", response=List[BookingOut])
def my_bookings(request):
    return Booking.objects.filter(user=request.user).order_by("-created_at")