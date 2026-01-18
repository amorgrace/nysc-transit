from datetime import datetime

from ninja import Schema


class BookingIn(Schema):  # → what the frontend must send
    trip_id: int
    seats: int = 1  # default 1 seat


class BookingOut(Schema):  # → what the API returns
    id: int
    trip_id: int
    seats: int
    total_price: float  # calculated by server
    status: str  # "pending", "confirmed", etc.
    created_at: datetime  # set by server
