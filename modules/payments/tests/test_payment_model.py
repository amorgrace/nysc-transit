import datetime
import re
from decimal import Decimal
from uuid import uuid4

import pytest

from modules.bookings.models import Booking
from modules.payments.models import Payment


@pytest.fixture
def vendor(USER):
    return USER.objects.create_user(
        email="vendor-payments@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        email_verified=True,
    )


@pytest.fixture
def corper(USER):
    return USER.objects.create_user(
        email="corper-payments@example.com",
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
        registration_number=f"PAY-{uuid4().hex[:6].upper()}",
        vehicle_type=vehicle_type,
        make_model="Toyota Hiace 2020",
        capacity=10,
        status="active",
    )


@pytest.fixture
def trip(vendor, vehicle):
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


@pytest.fixture
def booking(corper, trip):
    return Booking.objects.create(
        user=corper,
        trip=trip,
        selected_seats=1,
    )


@pytest.mark.django_db
def test_payment_reference_generated_on_create(corper, booking):
    payment = Payment.objects.create(
        user=corper,
        booking=booking,
        amount=Decimal("1000.00"),
        status="paid",
    )

    assert payment.payment_reference
    assert re.match(r"^[A-Z]-[A-F0-9]{10}$", payment.payment_reference)


@pytest.mark.django_db
def test_payment_reference_not_changed_on_update(corper, booking):
    payment = Payment.objects.create(
        user=corper,
        booking=booking,
        amount=Decimal("1500.00"),
        status="pending",
    )
    first_reference = payment.payment_reference

    payment.status = "paid"
    payment.save(update_fields=["status"])
    payment.refresh_from_db()

    assert payment.payment_reference == first_reference


@pytest.mark.django_db
def test_payment_references_are_distinct(corper, booking):
    payment_one = Payment.objects.create(
        user=corper,
        booking=booking,
        amount=Decimal("1000.00"),
        status="paid",
    )
    payment_two = Payment.objects.create(
        user=corper,
        booking=booking,
        amount=Decimal("2000.00"),
        status="paid",
    )

    assert payment_one.payment_reference != payment_two.payment_reference
