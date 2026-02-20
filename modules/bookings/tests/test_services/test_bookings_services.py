import uuid

import pytest
from django.http import Http404
from django.test import override_settings
from ninja.errors import HttpError

from modules.bookings.schemas import BookingIn
from modules.bookings.services.booking_service import (
    cancel_booking_service,
    create_booking_service,
    get_booking_service,
    get_my_bookings_service,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def vendor(USER):
    return USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        email_verified=True,
    )


@pytest.fixture
def corper(USER):
    return USER.objects.create_user(
        email="corper@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        email_verified=True,
    )


@pytest.fixture
def vehicle(vendor):
    from modules.trips.models import Vehicle, VehicleType

    vehicle_type = VehicleType.objects.create(name="Bus")
    return Vehicle.objects.create(
        vendor=vendor,
        registration_number="ABC-123XY",
        vehicle_type=vehicle_type,
        make_model="Toyota Hiace 2020",
        capacity=10,
        status="active",
    )


@pytest.fixture
def trip(vendor, vehicle):
    import datetime

    from modules.trips.models import Trip

    return Trip.objects.create(
        vendor=vendor,
        vehicle=vehicle,
        status="scheduled",
        departure_state="Lagos",
        departure_city="Iyana-Ipaja",
        destination_camp="NYSC Camp Iyana-Ipaja",
        departure_date=datetime.date.today(),
        departure_time=datetime.time(8, 0),
        price_per_seat=5000,
        available_seats=10,
    )


# ============================================================================
# CREATE BOOKING
# ============================================================================


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_create_booking_success(corper, trip):
    payload = BookingIn(trip_id=trip.id, selected_seats=2)
    resp = create_booking_service(corper, payload)

    assert resp.booking_status == "pending"
    assert resp.selected_seats == 2
    assert resp.trip == trip
    assert resp.user == corper


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_create_booking_not_enough_seats(corper, trip):
    payload = BookingIn(trip_id=trip.id, selected_seats=99)

    with pytest.raises(HttpError) as exc_info:
        create_booking_service(corper, payload)

    assert exc_info.value.status_code == 400
    assert "seats left" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_create_booking_trip_not_scheduled(corper, trip):
    trip.status = "cancelled"
    trip.save(update_fields=["status"])

    payload = BookingIn(trip_id=trip.id, selected_seats=1)

    with pytest.raises(Http404):
        create_booking_service(corper, payload)


# ============================================================================
# GET MY BOOKINGS
# ============================================================================


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_my_bookings(corper, trip):
    payload = BookingIn(trip_id=trip.id, selected_seats=1)
    create_booking_service(corper, payload)

    bookings = get_my_bookings_service(corper)
    assert len(bookings) == 1
    assert bookings[0].user == corper


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_my_bookings_empty(corper):
    bookings = get_my_bookings_service(corper)
    assert len(bookings) == 0


# ============================================================================
# GET SINGLE BOOKING
# ============================================================================


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_booking_success(corper, trip):
    payload = BookingIn(trip_id=trip.id, selected_seats=1)
    booking = create_booking_service(corper, payload)

    fetched = get_booking_service(corper, booking.id)
    assert fetched.id == booking.id


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_booking_not_found(corper):
    with pytest.raises(Http404):
        get_booking_service(corper, uuid.uuid4())


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_booking_wrong_user(corper, trip, USER):
    other_user = USER.objects.create_user(
        email="other@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        email_verified=True,
    )
    payload = BookingIn(trip_id=trip.id, selected_seats=1)
    booking = create_booking_service(corper, payload)

    with pytest.raises(Http404):
        get_booking_service(other_user, booking.id)


# ============================================================================
# CANCEL BOOKING
# ============================================================================


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_cancel_booking_success(corper, trip):
    payload = BookingIn(trip_id=trip.id, selected_seats=2)
    booking = create_booking_service(corper, payload)

    cancelled = cancel_booking_service(corper, booking.id)

    assert cancelled.booking_status == "cancelled"
    assert cancelled.cancelled_at is not None


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_cancel_already_cancelled_booking(corper, trip):
    payload = BookingIn(trip_id=trip.id, selected_seats=1)
    booking = create_booking_service(corper, payload)
    cancel_booking_service(corper, booking.id)

    with pytest.raises(HttpError) as exc_info:
        cancel_booking_service(corper, booking.id)

    assert exc_info.value.status_code == 400
    assert "already cancelled" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_cancel_completed_booking(corper, trip):
    payload = BookingIn(trip_id=trip.id, selected_seats=1)
    booking = create_booking_service(corper, payload)
    booking.booking_status = "completed"
    booking.save(update_fields=["booking_status"])

    with pytest.raises(HttpError) as exc_info:
        cancel_booking_service(corper, booking.id)

    assert exc_info.value.status_code == 400
    assert "Cannot cancel" in str(exc_info.value)
