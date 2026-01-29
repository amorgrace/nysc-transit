from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from ninja import Schema


class VehicleTypeSchema(Schema):
    name: str
    description: Optional[str] = None


class VehicleIn(Schema):
    registration_number: str
    vehicle_type: VehicleTypeSchema
    make_model: str
    color: Optional[str] = None
    capacity: int
    year_manufactured: Optional[int] = None
    is_insured: Optional[bool] = False
    insurance_expiry: Optional[date] = None


class VehicleOut(Schema):
    id: UUID
    registration_number: str
    vehicle_type: VehicleTypeSchema
    make_model: str
    color: Optional[str]
    capacity: int
    year_manufactured: Optional[int]
    status: str
    is_insured: bool
    insurance_expiry: Optional[date]


class TripIn(Schema):
    vehicle_id: UUID
    departure_city: str
    departure_state: str
    destination_camp: str
    departure_date: date
    departure_time: time
    estimated_arrival_time: Optional[time] = None
    price_per_seat: Decimal
    available_seats: int
    description: Optional[str] = None


class TripOut(Schema):
    id: int
    trip_id: UUID
    vehicle_id: UUID
    departure_city: str
    departure_state: str
    destination_camp: str
    departure_date: date
    departure_time: time
    estimated_arrival_time: Optional[time] = None
    price_per_seat: Decimal
    available_seats: int
    status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
