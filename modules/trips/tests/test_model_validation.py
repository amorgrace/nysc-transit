from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from modules.bookings.models import Booking
from modules.trips.models import Trip, Vehicle, VehicleType


@pytest.mark.django_db
def test_vehicle_status_and_insurance_and_roadworthy_properties():
    User = get_user_model()
    vendor = User.objects.create_user(
        email="vendor1@example.com",
        password="pass",
        role="vendor",
        full_name="Vendor One",
    )

    vt = VehicleType.objects.create(name="Minibus")

    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    v = Vehicle.objects.create(
        vendor=vendor,
        registration_number="ABC-123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=12,
        status="active",
        is_insured=True,
        insurance_expiry=tomorrow,
        roadworthiness_expiry_date=tomorrow,
    )

    assert v.is_active
    assert not v.is_inactive
    assert not v.is_under_maintenance
    assert v.is_insurance_valid
    assert v.is_roadworthy

    v.status = "maintenance"
    v.save()
    assert v.is_under_maintenance

    v.status = "inactive"
    v.save()
    assert v.is_inactive

    v.is_insured = True
    v.insurance_expiry = yesterday
    v.save()
    assert not v.is_insurance_valid

    v.roadworthiness_expiry_date = yesterday
    v.save()
    assert not v.is_roadworthy


@pytest.mark.django_db
def test_trip_properties_discounts_and_deadline():
    User = get_user_model()
    vendor = User.objects.create_user(
        email="vendor2@example.com",
        password="pass",
        role="vendor",
        full_name="Vendor Two",
    )

    vt = VehicleType.objects.create(name="Coach")

    vehicle = Vehicle.objects.create(
        vendor=vendor,
        registration_number="XYZ-999",
        vehicle_type=vt,
        make_model="Mercedes",
        color="Blue",
        capacity=40,
        status="active",
    )

    today = timezone.now().date()
    future = today + timedelta(days=7)
    past = today - timedelta(days=7)

    trip = Trip.objects.create(
        vendor=vendor,
        vehicle=vehicle,
        departure_state="Lagos",
        departure_city="Iyana-Ipaja",
        destination_camp="NYSC Camp",
        departure_date=today,
        departure_time=timezone.now().time(),
        price_per_seat=Decimal("2000.00"),
        available_seats=40,
        early_bird_discount_percentage=10,
        early_bird_deadline=future,
        group_discount_percentage=20,
    )

    assert trip.is_scheduled
    trip.status = "ongoing"
    trip.save()
    assert trip.is_ongoing
    trip.status = "completed"
    trip.save()
    assert trip.is_completed
    trip.status = "cancelled"
    trip.save()
    assert trip.is_cancelled

    # discount rates
    assert trip.group_discount_rate == Decimal("0.20")
    assert trip.early_bird_discount_rate == Decimal("0.10")

    # deadline not expired
    assert not trip.early_bird_deadline_expired
    trip.early_bird_deadline = past
    trip.save()
    assert trip.early_bird_deadline_expired


@pytest.mark.django_db
def test_total_seats_booked_and_available_remaining_and_clean_validations():
    User = get_user_model()
    vendor = User.objects.create_user(
        email="vendor3@example.com",
        password="pass",
        role="vendor",
        full_name="Vendor Three",
    )

    vt = VehicleType.objects.create(name="Bus")

    vehicle = Vehicle.objects.create(
        vendor=vendor,
        registration_number="BUS-001",
        vehicle_type=vt,
        make_model="Iveco",
        color="Green",
        capacity=10,
        status="active",
    )

    trip = Trip.objects.create(
        vendor=vendor,
        vehicle=vehicle,
        departure_state="Lagos",
        departure_city="Ikeja",
        destination_camp="NYSC Camp",
        departure_date=timezone.now().date(),
        departure_time=timezone.now().time(),
        price_per_seat=Decimal("1500.00"),
        available_seats=10,
    )

    # initially no bookings
    assert trip.total_seats_booked == 0
    assert trip.available_seats_remaining == 10

    # create bookings
    Booking.objects.create(user=vendor, trip=trip, selected_seats=2)
    Booking.objects.create(user=vendor, trip=trip, selected_seats=3)

    trip.refresh_from_db()
    assert trip.total_seats_booked == 5
    assert trip.available_seats_remaining == 5

    # clean validation: negative price
    trip.price_per_seat = Decimal("-10.00")
    with pytest.raises(ValidationError):
        trip.clean()

    # clean validation: capacity exceeded
    vehicle.capacity = 1
    vehicle.save()
    # create booking exceeding capacity
    Booking.objects.create(user=vendor, trip=trip, selected_seats=2)
    trip.refresh_from_db()
    with pytest.raises(ValidationError):
        trip.clean()
