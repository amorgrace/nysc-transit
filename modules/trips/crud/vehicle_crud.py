import logging

from django.db import IntegrityError
from ninja.errors import HttpError

from modules.trips.models import Vehicle
from modules.trips.schemas import VehicleIn

logger = logging.getLogger(__name__)


class VehicleCRUD:
    def __init__(self, queryset=None):
        self.model = Vehicle
        self.queryset = queryset or self.model.objects.all()

    def get_vehicle_by_id(self, vehicle_id, vendor=None):
        """Find Vehicle by id; optionally restrict by vendor"""
        qs = self.queryset
        if vendor is not None:
            qs = qs.filter(vendor=vendor)
        try:
            return qs.get(id=vehicle_id)
        except Vehicle.DoesNotExist as exc:
            logger.exception(f"Vehicle does not exist: {exc}")
            raise HttpError(404, "Vehicle does not exist")

    def create_vehicle(self, vendor, data: VehicleIn):
        """Create a vehicle for the given vendor"""
        vt = data.vehicle_type
        vt_name = None
        if isinstance(vt, dict):
            vt_name = vt.get("name")
        else:
            vt_name = getattr(vt, "name", None)

        vehicle_type_obj = None
        if vt_name:
            from modules.trips.models import VehicleType

            vehicle_type_obj, _ = VehicleType.objects.get_or_create(name=vt_name)

        try:
            vehicle = self.model.objects.create(
                vendor=vendor,
                registration_number=data.registration_number,
                vehicle_type=vehicle_type_obj,
                make_model=data.make_model,
                color=data.color,
                capacity=data.capacity,
                year_manufactured=data.year_manufactured,
                is_insured=data.is_insured or False,
                insurance_expiry=data.insurance_expiry,
            )
            return vehicle
        except IntegrityError as exc:
            logger.exception(f"Could not create vehicle: {exc}")
            raise HttpError(400, "Could not create vehicle")

    def update_vehicle(self, vendor, vehicle_id, data: VehicleIn):
        """Update Vehicle for a given vendor"""
        try:
            vehicle = self.get_vehicle_by_id(vehicle_id=vehicle_id, vendor=vendor)
            update_data = data.dict(exclude_unset=True)

            vt = update_data.pop("vehicle_type", None)
            if vt is not None:
                vt_name = None
                if isinstance(vt, dict):
                    vt_name = vt.get("name")
                else:
                    vt_name = getattr(vt, "name", None)
                if vt_name:
                    from modules.trips.models import VehicleType

                    vehicle_type_obj, _ = VehicleType.objects.get_or_create(
                        name=vt_name
                    )
                    setattr(vehicle, "vehicle_type", vehicle_type_obj)

            for field, value in update_data.items():
                setattr(vehicle, field, value)
            vehicle.save()
            return vehicle
        except IntegrityError as exc:
            logger.exception(f"Could not update vehicle: {exc}")
            raise HttpError(400, "Could not update vehicle")
        except Exception as exc:
            logger.exception(f"Unexpected error while updating vehicle: {exc}")
            raise HttpError(400, "Could not update vehicle")

    def delete_vehicle(self, vendor, vehicle_id):
        """Delete a vehicle belonging to a vendor"""
        try:
            vehicle = self.get_vehicle_by_id(vehicle_id=vehicle_id, vendor=vendor)
            vehicle.delete()
            return True
        except Vehicle.DoesNotExist as exc:
            logger.exception(f"Vehicle does not exist: {exc}")
            raise HttpError(404, "Vehicle does not exist")
        except Exception as exc:
            logger.exception(f"Could not delete vehicle: {exc}")
            raise HttpError(400, "Could not delete vehicle")
