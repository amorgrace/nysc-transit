from typing import List

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
