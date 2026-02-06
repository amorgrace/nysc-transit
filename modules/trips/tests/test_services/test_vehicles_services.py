import pytest

from modules.trips.models import Vehicle, VehicleType
from modules.trips.schemas import VehicleIn
from modules.trips.services.vehicle_services import VehicleService


@pytest.mark.django_db
def test_vehicle_service_update_and_delete(USER):
    vendor = USER.objects.create_user(
        email="vs1@example.com", password="pass", role="vendor"
    )

    vt = VehicleType.objects.create(name="bus")
    vehicle = Vehicle.objects.create(
        vendor=vendor,
        registration_number="SERV1",
        vehicle_type=vt,
        make_model="ModelX",
        capacity=10,
    )

    svc = VehicleService()

    data = VehicleIn(
        registration_number="SERV1",
        vehicle_type={"name": "bus"},
        make_model="ModelX Updated",
        color="Blue",
        capacity=12,
        year_manufactured=2020,
        is_insured=False,
    )

    updated = svc.update_vehicle(vendor, vehicle.id, data)
    assert updated.make_model == "ModelX Updated"
    assert updated.capacity == 12

    deleted = svc.delete_vehicle(vendor, vehicle.id)
    assert deleted is True
    with pytest.raises(Vehicle.DoesNotExist):
        Vehicle.objects.get(id=vehicle.id)
