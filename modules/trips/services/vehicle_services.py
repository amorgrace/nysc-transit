from typing import List

from modules.trips.crud.vehicle_crud import VehicleCRUD
from modules.trips.models import Vehicle
from modules.trips.schemas import VehicleIn


class VehicleService:
    def create_vehicle(self, vendor, data: VehicleIn):
        crud = VehicleCRUD()
        return crud.create_vehicle(vendor, data)

    def list_my_vehicles(self, vendor) -> List[Vehicle]:
        return list(Vehicle.objects.filter(vendor=vendor))
