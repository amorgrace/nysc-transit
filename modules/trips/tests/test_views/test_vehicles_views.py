from datetime import date, timedelta

import pytest
from django.test import override_settings

from modules.trips.models import Vehicle, VehicleType
from modules.trips.schemas import VehicleIn
from modules.trips.views.vehicles_views import (
    create_vehicle,
    delete_vehicle,
    list_my_vehicles,
    update_vehicle,
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
        vehicle_type={"name": "bus"},
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_of_manufacture=2020,
        is_insured=True,
        insurance_expiry=date.today() + timedelta(days=365),
    )

    resp = create_vehicle(request, data)
    assert resp.registration_number == "ABC123"
    assert resp.vehicle_type.name == "bus"
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

    vt_bus = VehicleType.objects.create(name="bus")
    vt_car = VehicleType.objects.create(name="car")

    Vehicle.objects.create(
        vendor=user,
        registration_number="ABC123",
        vehicle_type=vt_bus,
        make_model="Toyota Hiace",
        color="White",
        capacity=14,
        year_manufactured=2020,
    )

    Vehicle.objects.create(
        vendor=user,
        registration_number="XYZ789",
        vehicle_type=vt_car,
        make_model="Honda Accord",
        color="Black",
        capacity=4,
        year_manufactured=2019,
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
def test_update_and_delete_vehicle_view(USER):
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
        registration_number="UPDAT01",
        vehicle_type={"name": "bus"},
        make_model="Make",
        color="White",
        capacity=6,
        year_manufactured=2018,
    )

    created = create_vehicle(request, data)
    assert created.registration_number == "UPDAT01"

    payload = VehicleIn(
        registration_number="UPDAT01",
        vehicle_type={"name": "bus"},
        make_model="Make Updated",
        color="Red",
        capacity=8,
        year_manufactured=2018,
    )

    updated = update_vehicle(request, created.id, payload)
    assert updated.make_model == "Make Updated"

    # delete
    res = delete_vehicle(request, created.id)
    assert res is True or res is None
    from modules.trips.models import Vehicle as V

    with pytest.raises(V.DoesNotExist):
        V.objects.get(id=created.id)
