from typing import List
from uuid import UUID

from ninja import Router
from ninja_jwt.authentication import JWTAuth

from ..schemas import VehicleIn, VehicleOut
from ..services.vehicle_services import VehicleService

router = Router(tags=["Vehicles"], auth=JWTAuth())

vehicle_service = VehicleService()


@router.post("/", response=VehicleOut)
def create_vehicle(request, payload: VehicleIn):
    return vehicle_service.create_vehicle(request.user, payload)


@router.get("/", response=List[VehicleOut])
def list_my_vehicles(request):
    return vehicle_service.list_my_vehicles(request.user)


@router.patch("/{vehicle_id}", response=VehicleOut)
def update_vehicle(request, vehicle_id: UUID, payload: VehicleIn):
    return vehicle_service.update_vehicle(request.user, vehicle_id, payload)


@router.delete("/{vehicle_id}")
def delete_vehicle(request, vehicle_id: UUID):
    return vehicle_service.delete_vehicle(request.user, vehicle_id)
