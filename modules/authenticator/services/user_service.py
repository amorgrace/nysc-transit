from ninja.errors import HttpError

from modules.authenticator.schema import UserOutSchema
from modules.corper.schemas import CorperProfileOut
from modules.vendor.schemas import VendorProfileOut


def get_current_user_service(user):
    if not user:
        raise HttpError(401, "Authentication required")

    corper_profile = None
    vendor_profile = None

    if user.role == "corper":
        corper = getattr(user, "corper_profile", None)
        if corper:
            corper_profile = CorperProfileOut(
                phone=corper.phone,
                state_code=corper.state_code,
                call_up_number=corper.call_up_number,
                deployment_state=corper.deployment_state,
                camp_location=corper.camp_location,
                deployment_date=corper.deployment_date,
            )

    elif user.role == "vendor":
        vendor = getattr(user, "vendor_profile", None)
        if vendor:
            vendor_profile = VendorProfileOut(
                phone=vendor.phone,
                business_name=vendor.business_name,
                business_registration_number=vendor.business_registration_number,
                years_in_operation=vendor.years_in_operation,
                logo_url=vendor.logo_url,
                verification_status=vendor.verification_status,
                rejection_reason=vendor.rejection_reason,
                rating_average=vendor.rating_average,
            )

    return UserOutSchema(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        phone=user.phone,
        is_active=user.is_active,
        email_verified=user.email_verified,
        corper_profile=corper_profile,
        vendor_profile=vendor_profile,
    )
