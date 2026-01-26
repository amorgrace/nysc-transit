from datetime import date
from typing import List, Optional
from uuid import UUID

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

from modules.authenticator.permissions import vendor_required

from .models import Trip, Vehicle
from .models import Vendor as VendorProfile
from .schemas import (
    TripIn,
    TripOut,
    VehicleIn,
    VehicleOut,
    VendorProfileIn,
    VendorProfileOut,
)

router = Router(tags=["Vehicles & Trips"], auth=JWTAuth())


router = Router(auth=JWTAuth(), tags=["Vendor"])


@router.post("/vehicles", response=VehicleOut)
@vendor_required
def create_vehicle(request, payload: VehicleIn):
    # payload should now match the model fields
    vehicle = Vehicle.objects.create(
        vendor=request.user,  # ← vendor, not owner
        registration_number=payload.registration_number,
        vehicle_type=payload.vehicle_type,
        make_model=payload.make_model,
        color=payload.color,
        capacity=payload.capacity,
        year_of_manufacture=payload.year_of_manufacture,
        # status defaults to 'active' — no need to set unless you want to override
        is_insured=payload.is_insured or False,
        insurance_expiry=payload.insurance_expiry,
    )

    return vehicle


@router.get("/vehicles", response=List[VehicleOut])
@vendor_required
def list_my_vehicles(request):
    return Vehicle.objects.filter(vendor=request.user)


@router.post("/trips", response=TripOut)
@vendor_required
def create_trip(request, payload: TripIn):
    """
    Create a new trip for the authenticated vendor
    """
    vehicle = get_object_or_404(Vehicle, id=payload.vehicle_id, vendor=request.user)

    if payload.available_seats <= 0:
        raise HttpError(400, "Available seats must be greater than zero")

    # Optional: basic time logic check (you can expand this)
    if (
        payload.estimated_arrival_time
        and payload.departure_time >= payload.estimated_arrival_time
    ):
        raise HttpError(400, "Estimated arrival time must be after departure time")

    trip = Trip.objects.create(
        vendor=request.user,
        vehicle=vehicle,
        origin=payload.origin,
        destination=payload.destination,
        departure_date=payload.departure_date,
        departure_time=payload.departure_time,
        estimated_arrival_time=payload.estimated_arrival_time,
        price_per_seat=payload.price_per_seat,
        available_seats=payload.available_seats,
        description=payload.description,
        # status defaults to 'scheduled'
    )

    return trip


@router.get("/trips", response=list[TripOut])
@vendor_required
def list_my_trips(request):
    """
    List all trips created by the authenticated vendor
    """
    trips = request.user.trips.all().order_by("departure_date", "departure_time")
    return trips


@router.get("/trips/{trip_id}", response=TripOut)
@vendor_required
def get_trip(request, trip_id: UUID):
    trip = get_object_or_404(Trip, trip_id=trip_id, vendor=request.user)
    return trip


# Optional: Public search (no authentication)
@router.get("/search", response=list[TripOut], auth=None)
def search_trips(
    request,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    date: Optional[date] = None,
):
    qs = Trip.objects.filter(status="scheduled")

    if origin:
        qs = qs.filter(origin__icontains=origin)
    if destination:
        qs = qs.filter(destination__icontains=destination)
    if date:
        qs = qs.filter(departure_date=date)

    return qs.order_by("departure_date", "departure_time")


@router.get("/profile", response=dict)  # for now – you can create a proper schema later
@vendor_required
def get_vendor_profile(request):
    try:
        profile = request.user.vendor_profile
    except VendorProfile.DoesNotExist:
        raise HttpError(404, "Vendor profile not found")

    return {
        "email": request.user.email,
        "full_name": request.user.full_name,
        "role": request.user.role,
        "phone": profile.phone,
        "business_name": profile.business_name,
        "business_registration_number": profile.business_registration_number,
        "years_in_operation": profile.years_in_operation,
    }


@router.patch("/profile", response=VendorProfileOut)
@vendor_required
def update_vendor_profile(request, payload: VendorProfileIn):
    try:
        profile = request.user.vendor_profile
    except VendorProfile.DoesNotExist:
        raise HttpError(404, "Profile not found")

    update_data = payload.dict(exclude_unset=True)

    for attr, value in update_data.items():
        setattr(profile, attr, value)

    profile.save()
    return profile
