from datetime import date, time
from decimal import Decimal

import pytest

from modules.trips.models import Trip, Vehicle, VehicleType
from modules.trips.schemas import TripIn
from modules.trips.services.trip_services import TripService


@pytest.mark.django_db
def test_create_get_delete_trip(USER):
    vendor = USER.objects.create_user(
        "vendor1@example.com", password="pass", role="vendor"
    )

    vt = VehicleType.objects.create(name="MiniBus")

    vehicle = Vehicle.objects.create(
        vendor=vendor,
        registration_number="ABC-123",
        vehicle_type=vt,
        make_model="Toyota Hiace 2020",
        capacity=20,
    )

    svc = TripService()

    data = TripIn(
        vehicle_id=vehicle.id,
        departure_city="Iyana-Ipaja",
        departure_state="Lagos",
        destination_camp="NYSC Camp",
        departure_date=date.today(),
        departure_time=time(9, 0),
        estimated_arrival_time=time(12, 0),
        price_per_seat=Decimal("1500.00"),
        available_seats=10,
        description="Test trip",
    )

    trip = svc.create_trip(vendor, data)
    assert trip.vendor == vendor
    assert trip.vehicle == vehicle

    got = svc.get_trip(vendor, trip.id)
    assert got.id == trip.id

    # delete
    assert svc.delete_trip(vendor, trip.id) is True
    with pytest.raises(Trip.DoesNotExist):
        Trip.objects.get(id=trip.id)


@pytest.mark.django_db
def test_update_trip_signature_issue_exposed(USER):
    """The service currently passes args in the wrong order to CRUD.update_trip; expect a failure."""
    vendor = USER.objects.create_user(
        "vendor2@example.com", password="pass", role="vendor"
    )

    vt2 = VehicleType.objects.create(name="Coach")

    vehicle = Vehicle.objects.create(
        vendor=vendor,
        registration_number="XYZ-789",
        vehicle_type=vt2,
        make_model="Ford Transit",
        capacity=30,
    )

    trip = Trip.objects.create(
        vendor=vendor,
        vehicle=vehicle,
        departure_city="Origin",
        departure_state="State",
        destination_camp="Dest",
        departure_date=date.today(),
        departure_time=time(8, 0),
        estimated_arrival_time=time(11, 0),
        price_per_seat=Decimal("2000.00"),
        available_seats=5,
    )

    svc = TripService()

    update_data = TripIn(
        vehicle_id=vehicle.id,
        departure_city="NewOrigin",
        departure_state="State",
        destination_camp="Dest",
        departure_date=date.today(),
        departure_time=time(8, 0),
        estimated_arrival_time=time(11, 0),
        price_per_seat=Decimal("2000.00"),
        available_seats=5,
    )

    # update should now succeed after fixing argument ordering
    updated = svc.update_trip(vendor, trip.id, update_data)
    assert updated.departure_city == "NewOrigin"


@pytest.mark.django_db
def test_vendor_qs_ordering_and_filters(USER):
    vendor1 = USER.objects.create_user("v1@example.com", password="pass", role="vendor")
    vendor2 = USER.objects.create_user("v2@example.com", password="pass", role="vendor")

    vt3 = VehicleType.objects.create(name="Type1")
    vt4 = VehicleType.objects.create(name="Type2")

    vehicle1 = Vehicle.objects.create(
        vendor=vendor1,
        registration_number="AA-111",
        vehicle_type=vt3,
        make_model="M1",
        capacity=10,
    )
    vehicle2 = Vehicle.objects.create(
        vendor=vendor2,
        registration_number="BB-222",
        vehicle_type=vt4,
        make_model="M2",
        capacity=12,
    )

    # two trips for vendor1, one scheduled and one ongoing
    t1 = Trip.objects.create(
        vendor=vendor1,
        vehicle=vehicle1,
        departure_city="CityA",
        departure_state="StateA",
        destination_camp="CampA",
        departure_date=date.today(),
        departure_time=time(9, 0),
        price_per_seat=Decimal("1000.00"),
        available_seats=5,
        status="scheduled",
    )
    t2 = Trip.objects.create(
        vendor=vendor1,
        vehicle=vehicle1,
        departure_city="CityB",
        departure_state="StateA",
        destination_camp="CampB",
        departure_date=date.today(),
        departure_time=time(10, 0),
        price_per_seat=Decimal("1200.00"),
        available_seats=3,
        status="ongoing",
    )

    # one scheduled trip for vendor2
    t3 = Trip.objects.create(
        vendor=vendor2,
        vehicle=vehicle2,
        departure_city="CityA",
        departure_state="StateB",
        destination_camp="CampA",
        departure_date=date.today(),
        departure_time=time(7, 0),
        price_per_seat=Decimal("900.00"),
        available_seats=4,
        status="scheduled",
    )

    svc = TripService()

    # vendor_qs and list_my_trips
    qs_v1 = svc.vendor_qs(vendor1)
    assert qs_v1.count() == 2

    ordered = svc.list_my_trips(vendor1)
    # ordered by departure_time for same date -> t1 then t2
    assert list(ordered.values_list("id", flat=True)) == [t1.id, t2.id]

    # apply_status_filter
    scheduled_only = svc.apply_status_filter(qs_v1, "scheduled")
    assert list(scheduled_only) == [t1]

    multi_status = svc.apply_status_filter(qs_v1, ["scheduled", "ongoing"])
    assert multi_status.count() == 2

    # search_trips should only return trips with status scheduled
    res = svc.search_trips(departure_city="CityA")
    # t1 and t3 are scheduled and have CityA; ordering should place earlier date/time first
    ids = list(res.values_list("id", flat=True))
    assert t3.id in ids and t1.id in ids

    # filter_trips_by_status default 'scheduled' for vendor1 -> only t1
    f = svc.filter_trips_by_status(vendor1)
    assert list(f) == [t1]
