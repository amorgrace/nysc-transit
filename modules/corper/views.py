from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth

from modules.authenticator.permissions import corper_required

from .models import CorperProfile
from .schemas import CorperProfileIn, CorperProfileOut

router = Router(tags=["Corper Profile"], auth=JWTAuth())


@router.get("/profile", response=dict)  # or create a proper combined schema later
@corper_required
def get_corper_profile(request):
    try:
        profile = request.user.corper_profile

        return {
            # User details
            "email": request.user.email,
            "full_name": request.user.full_name,
            "role": request.user.role,
            "user_phone": request.user.phone,  # from User model (if exists)
            # CorperProfile details
            "corper_phone": profile.phone,
            "state_code": profile.state_code,
            "call_up_number": profile.call_up_number,
            "deployment_state": profile.deployment_state,
            "camp_location": profile.camp_location,
            "deployment_date": profile.deployment_date.isoformat(),
        }

    except CorperProfile.DoesNotExist:
        raise HttpError(404, "Corper profile not found")


@router.patch("/profile", response=CorperProfileOut)
@corper_required
def update_corper_profile(request, payload: CorperProfileIn):
    try:
        profile = request.user.corper_profile
    except CorperProfile.DoesNotExist:
        raise HttpError(404, "Profile not found")

    # Update only provided fields
    update_data = payload.dict(exclude_unset=True)

    # Optional: add validation for fields that shouldn't change after creation
    if "state_code" in update_data or "call_up_number" in update_data:
        raise HttpError(400, "State code and call-up number cannot be changed")

    for attr, value in update_data.items():
        setattr(profile, attr, value)

    profile.save()
    return profile
