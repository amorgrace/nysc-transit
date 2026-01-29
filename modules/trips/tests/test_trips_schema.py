from datetime import date, time
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic_core._pydantic_core import ValidationError

from modules.trips.schemas import TripIn, TripOut, VehicleIn, VehicleOut


def test_vehicle_in_valid():
    data = VehicleIn(
        registration_number="ABC123",
        vehicle_type={"name": "bus"},
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
        is_insured=True,
        insurance_expiry=date(2025, 12, 31),
    )
    assert data.registration_number == "ABC123"
    assert getattr(data.vehicle_type, "name", None) == "bus"
    assert data.capacity == 14


def test_vehicle_in_minimal():
    data = VehicleIn(
        registration_number="XYZ789",
        vehicle_type={"name": "car"},
        make_model="Honda Accord",
        capacity=4,
    )
    assert data.registration_number == "XYZ789"
    assert data.color is None
    assert data.is_insured is False


"""def test_vehicle_in_missing_required():
    with pytest.raises(ValidationError):
        VehicleIn(
            registration_number="ABC123",
            vehicle_type="bus",
            # missing make_model and capacity
        )"""


def test_vehicle_out_valid():
    vehicle_id = uuid4()
    data = VehicleOut(
        id=vehicle_id,
        registration_number="ABC123",
        vehicle_type={"name": "bus"},
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
        status="active",
        is_insured=True,
        insurance_expiry=date(2025, 12, 31),
    )
    assert data.id == vehicle_id
    assert data.status == "active"
    assert getattr(data.vehicle_type, "name", None) == "bus"


def test_trip_in_valid():
    vehicle_id = uuid4()
    data = TripIn(
        vehicle_id=vehicle_id,
        departure_state="Lagos",
        departure_city="Ajah",
        destination_camp="Abuja",
        departure_date=date(2025, 2, 1),
        departure_time=time(8, 0),
        estimated_arrival_time=time(20, 0),
        price_per_seat=Decimal("5000.00"),
        available_seats=10,
        description="Express trip",
    )
    assert data.departure_state == "Lagos"
    assert data.price_per_seat == Decimal("5000.00")
    assert data.available_seats == 10


def test_trip_in_minimal():
    vehicle_id = uuid4()
    data = TripIn(
        vehicle_id=vehicle_id,
        departure_city="Ajah",
        departure_state="Lagos",
        destination_camp="Abuja",
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
            departure_state="Lagos",
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
        departure_city="Ajah",
        departure_state="Lagos",
        destination_camp="Abuja",
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
