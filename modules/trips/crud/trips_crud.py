import logging

from django.db import IntegrityError
from ninja.errors import HttpError

from modules.trips.models import Trip
from modules.trips.schemas import TripIn

from .vehicle_crud import VehicleCRUD

logger = logging.getLogger(__name__)


class TripCRUD:
    def __init__(self, queryset=None):
        self.model = Trip
        self.queryset = queryset or self.model.objects.all()

    def get_trip_by_id(self, trip_id):
        """Find trip by id"""
        try:
            return self.queryset.get(id=trip_id)
        except Trip.DoesNotExist as exc:
            logger.exception(f"Trip does not exist: {exc}")
            raise HttpError(404, "Trip does not exist")

    def create_trip(self, vendor, data: TripIn):
        """Create a trip for a specific vendor"""

        vehicle = VehicleCRUD().get_vehicle_by_id(data.vehicle_id, vendor=vendor)

        if data.available_seats <= 0:
            raise HttpError(400, "Available seats must be greater than zero")

        if (
            data.estimated_arrival_time
            and data.departure_time >= data.estimated_arrival_time
        ):
            raise HttpError(400, "Estimated arrival time must be after departure time")

        try:
            trip_data = self.model.objects.create(
                vendor=vendor,
                vehicle=vehicle,
                departure_city=data.departure_city,
                departure_state=data.departure_state,
                destination_camp=data.destination_camp,
                departure_date=data.departure_date,
                departure_time=data.departure_time,
                estimated_arrival_time=data.estimated_arrival_time,
                price_per_seat=data.price_per_seat,
                available_seats=data.available_seats,
                description=data.description,
            )
            return trip_data
        except IntegrityError as exc:
            logger.exception(f"Could not create trip: {exc}")
            raise HttpError(400, "Could not create trip")
