from datetime import date
from typing import Optional
from uuid import UUID

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

from ..models import Trip, Vehicle
from ..schemas import TripIn, TripOut

router = Router(tags=["Trips"], auth=JWTAuth())


@router.post("/", response=TripOut)
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
        departure_city=payload.departure_city,
        departure_state=payload.departure_state,
        destination_camp=payload.destination_camp,
        departure_date=payload.departure_date,
        departure_time=payload.departure_time,
        estimated_arrival_time=payload.estimated_arrival_time,
        price_per_seat=payload.price_per_seat,
        available_seats=payload.available_seats,
        description=payload.description,
        # status defaults to 'scheduled'
    )

    return trip


@router.get("/", response=list[TripOut])
def list_my_trips(request):
    """
    List all trips created by the authenticated vendor
    """
    trips = request.user.trips.all().order_by("departure_date", "departure_time")
    return trips


@router.get("/{trip_id}", response=TripOut)
def get_trip(request, trip_id: UUID):
    trip = get_object_or_404(Trip, id=trip_id, vendor=request.user)
    return trip


# Optional: Public search (no authentication)
@router.get("/search", response=list[TripOut], auth=None)
def search_trips(
    request,
    departure_city: Optional[str] = None,
    departure_state: Optional[str] = None,
    destination_camp: Optional[str] = None,
    date: Optional[date] = None,
):
    qs = Trip.objects.filter(status="scheduled")

    if departure_state:
        qs = qs.filter(departure_state__icontains=departure_state)
    if departure_city:
        qs = qs.filter(departure_city__icontains=departure_city)
    if destination_camp:
        qs = qs.filter(destination_camp__icontains=destination_camp)
    if date:
        qs = qs.filter(departure_date=date)

    return qs.order_by("departure_date", "departure_time")
