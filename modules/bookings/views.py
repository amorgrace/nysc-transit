from typing import List

from ninja import Router
from ninja_jwt.authentication import JWTAuth

from .schemas import BookingIn, BookingOut
from .services.booking_service import (
    cancel_booking_service,
    create_booking_service,
    get_booking_service,
    get_my_bookings_service,
)

router = Router(tags=["Bookings"], auth=JWTAuth())


@router.post("/", response=BookingOut)
def create_booking(request, payload: BookingIn):
    return create_booking_service(request.user, payload)


@router.get("/", response=List[BookingOut])
def my_bookings(request):
    return get_my_bookings_service(request.user)


@router.get("/{booking_id}", response=BookingOut)
def get_booking(request, booking_id: int):
    return get_booking_service(request.user, booking_id)


@router.patch("/{booking_id}/cancel", response=BookingOut)
def cancel_booking(request, booking_id: int):
    return cancel_booking_service(request.user, booking_id)
