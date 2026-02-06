from datetime import date
from typing import Optional
from uuid import UUID

from ninja import Router
from ninja_jwt.authentication import JWTAuth

from ..schemas import TripIn, TripOut
from ..services.trip_services import TripService

trip_service = TripService()

router = Router(tags=["Trips"], auth=JWTAuth())


@router.post("/", response=TripOut)
def create_trip(request, payload: TripIn):
    """
    Create a new trip for the authenticated vendor
    """
    return trip_service.create_trip(request.user, payload)


@router.get("/", response=list[TripOut])
def list_my_trips(request):
    """
    List all trips created by the authenticated vendor
    """
    return trip_service.list_my_trips(request.user)


@router.get("/{trip_id}", response=TripOut)
def get_trip(request, trip_id: UUID):
    return trip_service.get_trip(request.user, trip_id)


@router.patch("/{trip_id}", response=TripOut)
def update_trip(request, trip_id: UUID, payload: TripIn):
    """Update an existing trip for the authenticated vendor.

    Args:
        request: The HTTP request (contains the authenticated user as request.user).
        trip_id (UUID): ID of the trip to update.
        payload (TripIn): Fields to update.

    Returns:
        TripOut: The updated trip.
    """
    return trip_service.update_trip(vendor=request.user, trip_id=trip_id, data=payload)


@router.delete("/{trip_id}")
def delete_trip(request, trip_id: UUID):
    """Delete a trip belonging to the authenticated vendor.

       This view delegates the deletion logic to trip_service.delete_trip, passing the
       authenticated user as the vendor and the provided trip_id.

        request (HttpRequest): Incoming HTTP request; request.user is expected to be the authenticated vendor.
        trip_id (UUID): UUID of the trip to delete.

        HttpResponse or rest_framework.response.Response: The response returned by trip_service.delete_trip, typically indicating success or failure.

    Raises:
        Exceptions propagated from trip_service.delete_trip (e.g. permission errors, not-found errors, validation errors).
    """
    return trip_service.delete_trip(vendor=request.user, trip_id=trip_id)


# Optional: Public search (no authentication)
@router.get("/search", response=list[TripOut], auth=None)
def search_trips(
    request,
    departure_city: Optional[str] = None,
    departure_state: Optional[str] = None,
    destination_camp: Optional[str] = None,
    date: Optional[date] = None,
):
    """Public trip search"""
    return trip_service.search_trips(
        departure_city=departure_city,
        departure_state=departure_state,
        destination_camp=destination_camp,
        dt=date,
    )


@router.get("/status", response=list[TripOut])
def search_trips_by_status(request, status: str):
    """
    Filter trips by status for the authenticated vendor
    """
    return trip_service.filter_trips_by_status(vendor=request.user, status=status)
