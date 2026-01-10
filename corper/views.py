from django.shortcuts import render

from ninja import Router
from ninja_jwt.authentication import JWTAuth
from authenticator.permissions import corper_required


router = Router(auth=JWTAuth())
# from ninja.security import PermissionBase

@router.get("/dashboard")
@corper_required 
def corper_dashboard(request):
    return {"message": "Welcome Corper"}