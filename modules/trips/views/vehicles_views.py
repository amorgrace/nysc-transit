from typing import List

from ninja import Router
from ninja_jwt.authentication import JWTAuth

from ..models import Vehicle, VehicleType
from ..schemas import VehicleIn, VehicleOut

router = Router(tags=["Vehicles"], auth=JWTAuth())


@router.post("/vehicles", response=VehicleOut)
def create_vehicle(request, payload: VehicleIn):
    # payload should now match the model fields
    # Resolve `vehicle_type` from the schema into a VehicleType model instance.
    vt = payload.vehicle_type
    vt_name = None
    if isinstance(vt, dict):
        vt_name = vt.get("name")
    else:
        # Ninja Schema instances and similar objects may expose a `name` attribute
        vt_name = getattr(vt, "name", None)

    vehicle_type_obj = None
    if vt_name:
        vehicle_type_obj, _ = VehicleType.objects.get_or_create(name=vt_name)

    vehicle = Vehicle.objects.create(
        vendor=request.user,  # ← vendor, not owner
        registration_number=payload.registration_number,
        vehicle_type=vehicle_type_obj,
        make_model=payload.make_model,
        color=payload.color,
        capacity=payload.capacity,
        year_manufactured=payload.year_manufactured,
        # status defaults to 'active' — no need to set unless you want to override
        is_insured=payload.is_insured or False,
        insurance_expiry=payload.insurance_expiry,
    )

    return vehicle


@router.get("/vehicles", response=List[VehicleOut])
def list_my_vehicles(request):
    return Vehicle.objects.filter(vendor=request.user)
