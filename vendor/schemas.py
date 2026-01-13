from ninja import Schema
from datetime import datetime
from typing import List, Optional

class VehicleIn(Schema):
    make: str
    model: str
    year: int
    license_plate: str
    capacity: int
    color: Optional[str] = None


class VehicleOut(Schema):
    id: int
    make: str
    model: str
    year: int
    license_plate: str
    capacity: int
    color: Optional[str]


class TripIn(Schema):
    vehicle_id: int
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price_per_seat: float
    available_seats: int


class TripOut(Schema):
    id: int
    vehicle_id: int
    origin: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    price_per_seat: float
    available_seats: int
    status: str


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