from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

from modules.authenticator.permissions import vendor_required
from modules.trips.views.trips_views import router as trips_router

from .models import Vendor as VendorProfile
from .schemas import VendorProfileIn, VendorProfileOut

router = Router(auth=JWTAuth(), tags=["Vendor"])
router.add_router("/trips", trips_router)
router.add_router("/vehicles", trips_router)


@router.get("/profile", response=dict)
@vendor_required
def get_vendor_profile(request):
    try:
        profile = request.user.vendor_profile
    except VendorProfile.DoesNotExist:
        raise HttpError(404, "Vendor profile not found")

    return {
        "email": request.user.email,
        "full_name": request.user.full_name,
        "role": request.user.role,
        "phone": profile.phone,
        "business_name": profile.business_name,
        "business_registration_number": profile.business_registration_number,
        "years_in_operation": profile.years_in_operation,
    }


@router.patch("/profile", response=VendorProfileOut)
@vendor_required
def update_vendor_profile(request, payload: VendorProfileIn):
    try:
        profile = request.user.vendor_profile
    except VendorProfile.DoesNotExist:
        raise HttpError(404, "Profile not found")

    update_data = payload.dict(exclude_unset=True)

    for attr, value in update_data.items():
        setattr(profile, attr, value)

    profile.save()
    return profile
