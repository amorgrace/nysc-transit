from datetime import date, time, timedelta

import pytest
from django.test import override_settings
from ninja.errors import HttpError

from modules.vendor.schemas import TripIn, VehicleIn, VendorProfileIn
from modules.vendor.views import (
    create_trip,
    create_vehicle,
    get_trip,
    get_vendor_profile,
    list_my_trips,
    list_my_vehicles,
    search_trips,
    update_vendor_profile,
)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_create_vehicle_success(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = VehicleIn(
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
        is_insured=True,
        insurance_expiry=date.today() + timedelta(days=365),
    )

    resp = create_vehicle(request, data)
    assert resp.registration_number == "ABC123"
    assert resp.vehicle_type == "bus"
    assert resp.capacity == 14


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_list_my_vehicles(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    from modules.vendor.models import Vehicle

    Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    Vehicle.objects.create(
        vendor=user,
        registration_number="XYZ789",
        vehicle_type="car",
        make_model="Honda Accord",
        color="Black",
        capacity=4,
        year_of_manufacture=2019,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = list_my_vehicles(request)
    assert len(resp) == 2
    assert resp[0].registration_number in ["ABC123", "XYZ789"]


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

    from modules.vendor.models import Vehicle

    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = TripIn(
        vehicle_id=vehicle.id,
        origin="Lagos",
        destination="Abuja",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        estimated_arrival_time=time(20, 0),
        price_per_seat=5000,
        available_seats=10,
        description="Express trip",
    )

    resp = create_trip(request, data)
    assert resp.origin == "Lagos"
    assert resp.destination == "Abuja"
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

    from modules.vendor.models import Vehicle

    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = TripIn(
        vehicle_id=vehicle.id,
        origin="Lagos",
        destination="Abuja",
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

    from modules.vendor.models import Vehicle

    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = TripIn(
        vehicle_id=vehicle.id,
        origin="Lagos",
        destination="Abuja",
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

    from modules.vendor.models import Trip, Vehicle

    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        origin="Lagos",
        destination="Abuja",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
    )

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        origin="Abuja",
        destination="Lagos",
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

    from modules.vendor.models import Trip, Vehicle

    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    trip = Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        origin="Lagos",
        destination="Abuja",
        departure_date=date.today() + timedelta(days=1),
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = get_trip(request, trip.trip_id)
    assert resp.trip_id == trip.trip_id
    assert resp.origin == "Lagos"


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

    from modules.vendor.models import Trip, Vehicle

    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        origin="Lagos",
        destination="Abuja",
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

    from modules.vendor.models import Trip, Vehicle

    vehicle = Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type="bus",
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
    )

    trip_date = date.today() + timedelta(days=1)

    Trip.objects.create(
        vendor=user,
        vehicle=vehicle,
        origin="Lagos",
        destination="Abuja",
        departure_date=trip_date,
        departure_time=time(8, 0),
        price_per_seat=5000,
        available_seats=10,
        status="scheduled",
    )

    resp = search_trips(object(), origin="Lagos", destination="Abuja", date=trip_date)
    assert len(resp) == 1
    assert resp[0].origin == "Lagos"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_vendor_profile_success(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    from modules.vendor.models import VendorProfile

    VendorProfile.objects.create(
        user=user,
        phone="08012345678",
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = get_vendor_profile(request)
    assert resp["email"] == "vendor@example.com"
    assert resp["business_name"] == "Acme Ltd"
    assert resp["phone"] == "08012345678"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_vendor_profile_not_found(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    with pytest.raises(HttpError) as exc_info:
        get_vendor_profile(request)
    assert exc_info.value.status_code == 404


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_vendor_profile_success(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    from modules.vendor.models import VendorProfile

    profile = VendorProfile.objects.create(
        user=user,
        phone="08012345678",
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = VendorProfileIn(
        description="We sell amazing things",
        years_in_operation=7,
    )

    resp = update_vendor_profile(request, data)
    assert resp.description == "We sell amazing things"
    assert resp.years_in_operation == 7

    profile.refresh_from_db()
    assert profile.description == "We sell amazing things"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_vendor_profile_not_found(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = VendorProfileIn(description="Updated description")

    with pytest.raises(HttpError) as exc_info:
        update_vendor_profile(request, data)
    assert exc_info.value.status_code == 404
