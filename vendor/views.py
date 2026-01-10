from django.shortcuts import render
from ninja import Router
from ninja_jwt.authentication import JWTAuth
from authenticator.permissions import vendor_required


router = Router(
    auth=JWTAuth(),
    tags=['Vendor']
)

@router.get("/dashboard")
@vendor_required                  
def vendor_dashboard(request):
    return {"message": "Welcome Vendor!"}