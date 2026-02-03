from typing import Optional

from ninja.errors import HttpError

from .crud import VendorCRUD
from .models import Vendor
from .schemas import VendorProfileIn


class VendorService:
    def __init__(self, crud: Optional[VendorCRUD] = None):
        self.crud = crud or VendorCRUD()

    def _get_profile(self, user):
        try:
            return user.vendor_profile
        except Vendor.DoesNotExist:
            raise HttpError(404, "Vendor profile not found")

    def get_profile_data(self, user) -> dict:
        """Return a serializable profile dict for the requesting user."""
        profile = self._get_profile(user)
        return {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "phone": profile.phone,
            "business_name": profile.business_name,
            "business_registration_number": profile.business_registration_number,
            "years_in_operation": profile.years_in_operation,
        }

    def update_profile(self, user, payload: VendorProfileIn):
        """Update vendor profile using CRUD layer. Returns updated model."""
        profile = self._get_profile(user)
        update_data = payload.dict(exclude_unset=True)
        if not update_data:
            return profile
        return self.crud.update_fields(data=payload, vendor_id=profile.id)

    def create_vendor(self, payload: VendorProfileIn, user=None):
        try:
            return self.crud.create_vendor(data=payload, user=user)
        except HttpError:
            raise
        except Exception as exc:
            raise HttpError(400, f"Unable to create vendor: {exc}")

    def verify_vendor(self, vendor_id):
        return self.crud.verify_vendor(vendor_id=vendor_id)

    def delete_vendor(self, vendor_id):
        return self.crud.delete_vendor(vendor_id=vendor_id)
