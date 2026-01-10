# app/app.py
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "engine.settings")
django.setup()

from ninja import NinjaAPI
from corper.views import router as corper_router
from vendor.views import router as vendor_router
from authenticator.views import router as auth_router


app = NinjaAPI()

app.add_router("/auth/", auth_router)
app.add_router("/corper/", corper_router)
app.add_router("/vendor/", vendor_router)
