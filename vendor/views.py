from django.shortcuts import render
from ninja import Router, Schema, Query
from ninja_jwt.authentication import JWTAuth
from authenticator.permissions import vendor_required
from vendor.models import Vehicle, Trip
from ninja.errors import HttpError
from .schemas import *
from typing import List, Optional
from datetime import date
from django.shortcuts import get_object_or_404
from .models import *

router = Router(tags=["Vehicles & Trips"], auth=JWTAuth())


router = Router(
    auth=JWTAuth(),
    tags=['Vendor']
)

@router.post("/vehicles", response=VehicleOut)
@vendor_required
def create_vehicle(request, payload: VehicleIn):
    vehicle = Vehicle.objects.create(
        owner=request.user,
        **payload.dict()
    )
    return vehicle


@router.get("/vehicles", response=List[VehicleOut])
@vendor_required
def list_my_vehicles(request):
    return Vehicle.objects.filter(owner=request.user)

@router.post("/trips", response=TripOut)
@vendor_required
def create_trip(request, payload: TripIn):
    vehicle = get_object_or_404(
        Vehicle,
        pk=payload.vehicle_id,
        owner=request.user
    )

    if payload.departure_time >= payload.arrival_time:
        raise HttpError(400, "Departure time must be before arrival time")

    trip = Trip.objects.create(
        vehicle=vehicle,
        **payload.dict(exclude={"vehicle_id"})
    )
    return trip


@router.get("/trips", response=List[TripOut], auth=None)
def search_trips(
    request,
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    date: Optional[date] = Query(None),
):
    qs = Trip.objects.filter(status="scheduled")

    if origin:
        qs = qs.filter(origin__icontains=origin)
    if destination:
        qs = qs.filter(destination__icontains=destination)
    if date:
        qs = qs.filter(departure_time__date=date)
    return qs   


@router.get("/profile", response=VendorProfileOut)
@vendor_required
def get_vendor_profile(request):
    try:
        profile = request.user.vendor_profile
        return profile
    except VendorProfile.DoesNotExist:
        raise HttpError(404, "Profile not found")


@router.patch("/profile", response=VendorProfileOut)
@vendor_required
def update_vendor_profile(request, payload: VendorProfileIn):
    try:
        profile = request.user.vendor_profile
    except VendorProfile.DoesNotExist:
        raise HttpError(404, "Profile not found")

    update_data = payload.dict(exclude_unset=True)

    # Example: you might allow changing description freely, but limit others
    for attr, value in update_data.items():
        setattr(profile, attr, value)

    profile.save()
    return profile