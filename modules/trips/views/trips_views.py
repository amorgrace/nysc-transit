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


# Optional: Public search (no authentication)
@router.get("/search", response=list[TripOut], auth=None)
def search_trips(
    request,
    departure_city: Optional[str] = None,
    departure_state: Optional[str] = None,
    destination_camp: Optional[str] = None,
    date: Optional[date] = None,
):
    return trip_service.search_trips(
        departure_city=departure_city,
        departure_state=departure_state,
        destination_camp=destination_camp,
        dt=date,
    )
