from datetime import date, time, timedelta

import pytest
from django.test import override_settings
from ninja.errors import HttpError

from modules.trips.models import Trip, Vehicle, VehicleType
from modules.trips.schemas import TripIn
from modules.trips.views.trips_views import (
    create_trip,
    get_trip,
    list_my_trips,
    search_trips,
)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_create_trip_success(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = TripIn(
        vehicle_id=vehicle.id,
        departure_city="Ajah",
        departure_state="Lagos",
        destination_camp="Abuja Camp",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        estimated_arrival_time=time(20, 0),
        price_per_seat=5000,
        available_seats=10,
        description="Express trip",
    )

    resp = create_trip(request, data)
    assert resp.departure_state == "Lagos"
    assert resp.destination_camp == "Abuja Camp"
    assert resp.available_seats == 10
    assert resp.price_per_seat == 5000


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_create_trip_invalid_seats(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = TripIn(
        vehicle_id=vehicle.id,
        departure_state="Lagos",
        departure_city="Ajah",
        destination_camp="Abuja Camp",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=0,
    )

    with pytest.raises(HttpError) as exc_info:
        create_trip(request, data)
    assert exc_info.value.status_code == 400


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_create_trip_invalid_times(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = TripIn(
        vehicle_id=vehicle.id,
        departure_state="Lagos",
        departure_city="Ajah",
        destination_camp="Abuja Camp",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(20, 0),
        estimated_arrival_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
    )

    with pytest.raises(HttpError) as exc_info:
        create_trip(request, data)
    assert exc_info.value.status_code == 400


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_list_my_trips(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        departure_state="Lagos",
        departure_city="Ajah",
        destination_camp="Abuja Camp",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
    )

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        departure_state="Abuja",
        departure_city="Abuja",
        destination_camp="Lagos Camp",
        departure_date=date.today() + timedelta(days=2),
        departure_time=time(9, 0),
        price_per_seat=5500,
        available_seats=12,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = list_my_trips(request)
    assert len(resp) == 2


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_trip_success(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    trip = Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        departure_state="Lagos",
        departure_city="Ajah",
        destination_camp="Abuja",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = get_trip(request, trip.id)
    assert resp.id == trip.id
    assert resp.departure_state == "Lagos"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_search_trips_all(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        departure_city="Ajah",
        departure_state="Lagos",
        destination_camp="Abuja",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
        status="scheduled",
    )

    resp = search_trips(object())
    assert len(resp) == 1


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_search_trips_with_filters(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    trip_date = date.today() + timedelta(days=1)

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        departure_city="Ajah",
        departure_state="Lagos",
        destination_camp="Abuja",
        departure_date=trip_date,
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
        status="scheduled",
    )

    resp = search_trips(
        object(), departure_state="Lagos", destination_camp="Abuja", date=trip_date
    )
    assert len(resp) == 1
    assert resp[0].departure_state == "Lagos"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_and_delete_trip_views(USER):
    user = USER.objects.create_user(
        email="vendor2@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="minibus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="UPD123",
        vehicle_type=vt,
        make_model="Toyota",
        capacity=16,
    )

    trip = Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        departure_state="Lagos",
        departure_city="Ikeja",
        destination_camp="Abuja",
        departure_date=date.today(),
        departure_time=time(9, 0),
        price_per_seat=3000,
        available_seats=8,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    # update trip via view
    payload = TripIn(
        vehicle_id=vehicle.id,
        departure_city="UpdatedCity",
        departure_state="Lagos",
        destination_camp="Abuja",
        departure_date=date.today(),
        departure_time=time(9, 0),
        estimated_arrival_time=time(12, 0),
        price_per_seat=3000,
        available_seats=8,
    )

    updated = __import__(  # call view function directly
        "modules.trips.views.trips_views", fromlist=["update_trip"]
    ).update_trip(request, trip.id, payload)
    assert updated.departure_city == "UpdatedCity"

    # delete via view
    deleted = __import__(
        "modules.trips.views.trips_views", fromlist=["delete_trip"]
    ).delete_trip(request, trip.id)
    assert deleted is True or deleted is None
    with pytest.raises(Trip.DoesNotExist):
        Trip.objects.get(id=trip.id)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_search_trips_by_status_view(USER):
    user = USER.objects.create_user(
        email="vendor3@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="STAT123",
        vehicle_type=vt,
        make_model="Model",
        capacity=20,
    )

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        departure_state="Lagos",
        departure_city="Ikeja",
        destination_camp="Abuja",
        departure_date=date.today(),
        departure_time=time(9, 0),
        price_per_seat=3000,
        available_seats=8,
        status="ongoing",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = __import__(
        "modules.trips.views.trips_views", fromlist=["search_trips_by_status"]
    ).search_trips_by_status(request, status="ongoing")
    assert len(resp) == 1
