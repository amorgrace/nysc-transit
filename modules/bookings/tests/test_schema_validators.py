import uuid
from datetime import datetime
from decimal import Decimal

import pytest

from modules.bookings.schemas import BookingIn, BookingOut

# ============================================================================
# BookingIn SCHEMA TESTS
# ============================================================================


def test_booking_in_valid():
    data = BookingIn(trip_id=uuid.uuid4(), selected_seats=2)
    assert data.selected_seats == 2


def test_booking_in_default_seats():
    data = BookingIn(trip_id=uuid.uuid4())
    assert data.selected_seats == 1


def test_booking_in_invalid_trip_id():
    with pytest.raises(Exception):
        BookingIn(trip_id="not-a-uuid", selected_seats=1)


def test_booking_in_invalid_seats():
    with pytest.raises(Exception):
        BookingIn(trip_id=uuid.uuid4(), selected_seats="many")


# ============================================================================
# BookingOut SCHEMA TESTS
# ============================================================================


def test_booking_out_valid():
    data = BookingOut(
        id=uuid.uuid4(),
        trip_id=uuid.uuid4(),
        selected_seats=2,
        total_price=Decimal("10000.00"),
        booking_status="pending",
        payment_status="pending",
        booked_at=datetime.now(),
    )
    assert data.booking_status == "pending"
    assert data.payment_status == "pending"
    assert data.selected_seats == 2


def test_booking_out_total_price_is_decimal():
    data = BookingOut(
        id=uuid.uuid4(),
        trip_id=uuid.uuid4(),
        selected_seats=1,
        total_price=Decimal("5000.00"),
        booking_status="confirmed",
        payment_status="paid",
        booked_at=datetime.now(),
    )
    assert isinstance(data.total_price, Decimal)


def test_booking_out_missing_required_field():
    with pytest.raises(Exception):
        BookingOut(
            id=uuid.uuid4(),
            trip_id=uuid.uuid4(),
            selected_seats=1,
            # missing total_price, booking_status, payment_status, booked_at
        )
