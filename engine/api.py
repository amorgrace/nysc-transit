from ninja import NinjaAPI
from corper.views import router as corper_router
from vendor.views import router as vendor_router
from authenticator.views import router as auth_router
from bookings.views import router as booking_router


api = NinjaAPI()

api.add_router("/auth/", auth_router)
api.add_router("/corper/", corper_router)
api.add_router("/vendor/", vendor_router)
api.add_router("/bookings/", booking_router)
