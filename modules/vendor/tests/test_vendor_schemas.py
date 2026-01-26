from datetime import date, time
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic_core._pydantic_core import ValidationError

from modules.vendor.schemas import (
    TripIn,
    TripOut,
    VehicleIn,
    VehicleOut,
    VendorProfileIn,
    VendorProfileOut,
)


def test_vehicle_in_valid():
    data = VehicleIn(
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
        is_insured=True,
        insurance_expiry=date(2025, 12, 31),
    )
    assert data.registration_number == "ABC123"
    assert data.vehicle_type == "bus"
    assert data.capacity == 14


def test_vehicle_in_minimal():
    data = VehicleIn(
        registration_number="XYZ789",
        vehicle_type="car",
        make_model="Honda Accord",
        capacity=4,
    )
    assert data.registration_number == "XYZ789"
    assert data.color is None
    assert data.is_insured is False


def test_vehicle_in_missing_required():
    with pytest.raises(ValidationError):
        VehicleIn(
            registration_number="ABC123",
            vehicle_type="bus",
            # missing make_model and capacity
        )


def test_vehicle_out_valid():
    vehicle_id = uuid4()
    data = VehicleOut(
        id=vehicle_id,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
        status="active",
        is_insured=True,
        insurance_expiry=date(2025, 12, 31),
    )
    assert data.id == vehicle_id
    assert data.status == "active"


def test_trip_in_valid():
    vehicle_id = uuid4()
    data = TripIn(
        vehicle_id=vehicle_id,
        origin="Lagos",
        destination="Abuja",
        departure_date=date(2025, 2, 1),
        departure_time=time(8, 0),
        estimated_arrival_time=time(20, 0),
        price_per_seat=Decimal("5000.00"),
        available_seats=10,
        description="Express trip",
    )
    assert data.origin == "Lagos"
    assert data.price_per_seat == Decimal("5000.00")
    assert data.available_seats == 10


def test_trip_in_minimal():
    vehicle_id = uuid4()
    data = TripIn(
        vehicle_id=vehicle_id,
        origin="Lagos",
        destination="Abuja",
        departure_date=date(2025, 2, 1),
        departure_time=time(8, 0),
        price_per_seat=Decimal("5000"),
        available_seats=10,
    )
    assert data.estimated_arrival_time is None
    assert data.description is None


def test_trip_in_missing_required():
    with pytest.raises(ValidationError):
        TripIn(
            vehicle_id=uuid4(),
            origin="Lagos",
            # missing destination, departure_date, etc.
        )


def test_trip_out_valid():
    from datetime import datetime

    trip_id = uuid4()
    vehicle_id = uuid4()
    now = datetime.now()

    data = TripOut(
        id=1,
        trip_id=trip_id,
        vehicle_id=vehicle_id,
        origin="Lagos",
        destination="Abuja",
        departure_date=date(2025, 2, 1),
        departure_time=time(8, 0),
        estimated_arrival_time=time(20, 0),
        price_per_seat=Decimal("5000.00"),
        available_seats=10,
        status="scheduled",
        description="Express trip",
        created_at=now,
        updated_at=now,
    )
    assert data.trip_id == trip_id
    assert data.status == "scheduled"


def test_vendor_profile_out_valid():
    data = VendorProfileOut(
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )
    assert data.business_name == "Acme Ltd"
    assert data.years_in_operation == 5


def test_vendor_profile_out_minimal():
    data = VendorProfileOut(
        business_name="Acme Ltd",
        years_in_operation=5,
    )
    assert data.business_registration_number is None
    assert data.description is None


def test_vendor_profile_out_missing_required():
    with pytest.raises(ValidationError):
        VendorProfileOut(
            business_name="Acme Ltd",
            # missing years_in_operation
        )


def test_vendor_profile_in_all_fields():
    data = VendorProfileIn(
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )
    assert data.business_name == "Acme Ltd"
    assert data.years_in_operation == 5


def test_vendor_profile_in_partial():
    data = VendorProfileIn(
        description="Updated description",
    )
    assert data.description == "Updated description"
    assert data.business_name is None
    assert data.years_in_operation is None


def test_vendor_profile_in_empty():
    data = VendorProfileIn()
    assert data.business_name is None
    assert data.business_registration_number is None
    assert data.years_in_operation is None
    assert data.description is None
