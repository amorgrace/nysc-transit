import uuid
from datetime import datetime
from decimal import Decimal

from ninja import Schema


class BookingIn(Schema):
    trip_id: uuid.UUID
    selected_seats: int = 1


class BookingOut(Schema):
    id: uuid.UUID
    trip_id: uuid.UUID
    selected_seats: int
    total_price: Decimal
    booking_status: str
    payment_status: str
    booked_at: datetime
