from typing import List
from uuid import UUID

from modules.trips.crud.vehicle_crud import VehicleCRUD
from modules.trips.models import Vehicle
from modules.trips.schemas import VehicleIn


class VehicleService:
    crud = VehicleCRUD()

    def create_vehicle(self, vendor, data: VehicleIn):
        return self.crud.create_vehicle(vendor, data)

    def list_my_vehicles(self, vendor) -> List[Vehicle]:
        return list(Vehicle.objects.filter(vendor=vendor))

    def update_vehicle(self, vendor, vehicle_id: UUID, data: VehicleIn):
        return self.crud.update_vehicle(vendor, vehicle_id, data)

    def delete_vehicle(self, vendor, vehicle_id: UUID):
        return self.crud.delete_vehicle(vendor, vehicle_id)
