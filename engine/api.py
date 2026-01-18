from ninja import NinjaAPI

from modules.authenticator.views import router as auth_router
from modules.bookings.views import router as booking_router
from modules.corper.views import router as corper_router
from modules.vendor.views import router as vendor_router

api = NinjaAPI()

api.add_router("/auth/", auth_router)
api.add_router("/corper/", corper_router)
api.add_router("/vendor/", vendor_router)
api.add_router("/bookings/", booking_router)
