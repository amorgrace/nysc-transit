from datetime import date
from typing import Optional

from modules.trips.crud.trips_crud import TripCRUD
from modules.trips.models import Trip
from modules.trips.schemas import TripIn


class TripService:
    def create_trip(self, vendor, data: TripIn):
        crud = TripCRUD(queryset=Trip.objects.filter(vendor=vendor))
        return crud.create_trip(vendor, data)

    def list_my_trips(self, vendor):
        return Trip.objects.filter(vendor=vendor).order_by(
            "departure_date", "departure_time"
        )

    def get_trip(self, vendor, trip_id):
        crud = TripCRUD(queryset=Trip.objects.filter(vendor=vendor))
        return crud.get_trip_by_id(trip_id)

    def search_trips(
        self,
        departure_city: Optional[str] = None,
        departure_state: Optional[str] = None,
        destination_camp: Optional[str] = None,
        dt: Optional[date] = None,
    ):
        qs = Trip.objects.filter(status="scheduled")

        if departure_state:
            qs = qs.filter(departure_state__icontains=departure_state)
        if departure_city:
            qs = qs.filter(departure_city__icontains=departure_city)
        if destination_camp:
            qs = qs.filter(destination_camp__icontains=destination_camp)
        if dt:
            qs = qs.filter(departure_date=dt)

        return qs.order_by("departure_date", "departure_time")
