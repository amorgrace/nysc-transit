from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from uuid import UUID

from ninja import Schema


class VehicleIn(Schema):
    registration_number: str
    vehicle_type: str  # must be one of: 'bus', 'minibus', 'van', 'car'
    make_model: str
    color: Optional[str] = None
    capacity: int
    year_of_manufacture: Optional[int] = None
    is_insured: Optional[bool] = False
    insurance_expiry: Optional[date] = None


class VehicleOut(Schema):
    id: UUID
    registration_number: str
    vehicle_type: str
    make_model: str
    color: Optional[str]
    capacity: int
    year_of_manufacture: Optional[int]
    status: str
    is_insured: bool
    insurance_expiry: Optional[date]


class TripIn(Schema):
    vehicle_id: UUID
    origin: str
    destination: str
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
    origin: str
    destination: str
    departure_date: date
    departure_time: time
    estimated_arrival_time: Optional[time] = None
    price_per_seat: Decimal
    available_seats: int
    status: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class VendorProfileOut(Schema):
    business_name: str
    business_registration_number: Optional[str] = None
    years_in_operation: int
    description: Optional[str] = None


class VendorProfileIn(Schema):
    business_name: Optional[str] = None
    business_registration_number: Optional[str] = None
    years_in_operation: Optional[int] = None
    description: Optional[str] = None
