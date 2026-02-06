from modules.trips.crud.trips_crud import TripCRUD
from modules.trips.models import Trip
from modules.trips.schemas import TripIn


class TripService:
    ORDERING = ("departure_date", "departure_time")

    def vendor_qs(self, vendor):
        return Trip.objects.filter(vendor=vendor)

    def ordered(self, qs):
        return qs.order_by(*self.ORDERING)

    def apply_status_filter(self, qs, status):
        if status is None:
            return qs
        if isinstance(status, (list, tuple, set)):
            return qs.filter(status__in=status)
        return qs.filter(status=status)

    def vendor_crud(self, vendor):
        return TripCRUD(queryset=self.vendor_qs(vendor))

    def create_trip(self, vendor, data: TripIn):
        return self.vendor_crud(vendor).create_trip(vendor, data)

    def list_my_trips(self, vendor):
        return self.ordered(self.vendor_qs(vendor))

    def get_trip(self, vendor, trip_id):
        return self.vendor_crud(vendor).get_trip_by_id(trip_id)

    def update_trip(self, vendor, trip_id, data: TripIn):
        # TripCRUD.update_trip expects (data, trip_id)
        return self.vendor_crud(vendor).update_trip(data, trip_id)

    def delete_trip(self, vendor, trip_id):
        return self.vendor_crud(vendor).delete_trip(trip_id)

    def search_trips(
        self,
        departure_city=None,
        departure_state=None,
        destination_camp=None,
        dt=None,
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

        return self.ordered(qs)

    def filter_trips_by_status(self, vendor, status="scheduled"):
        qs = self.vendor_qs(vendor)
        qs = self.apply_status_filter(qs, status)
        return self.ordered(qs)
