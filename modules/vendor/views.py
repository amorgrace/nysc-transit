from ninja import Router
from ninja_jwt.authentication import JWTAuth

from modules.authenticator.permissions import vendor_required
from modules.trips.views.trips_views import router as trips_router
from modules.trips.views.vehicles_views import router as vehicles_router

from .schemas import VendorProfileIn, VendorProfileOut
from .services import VendorService

router = Router(auth=JWTAuth(), tags=["Vendor"])
router.add_router("/trips", trips_router)
router.add_router("/vehicles", vehicles_router)

_service = VendorService()


@router.get("/profile", response=dict)
@vendor_required
def get_vendor_profile(request):
    return _service.get_profile_data(request.user)


@router.patch("/profile", response=VendorProfileOut)
@vendor_required
def update_vendor_profile(request, payload: VendorProfileIn):
    return _service.update_profile(request.user, payload)
