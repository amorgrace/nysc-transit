from django.conf import settings
from django.db import transaction
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.crud.vendor_crud import (
    business_number_exists,
    create_vendor_user,
    delete_user,
    email_exists,
    phone_exists,
)
from modules.authenticator.utils.email import (
    generate_otp,
    send_or_log_otp_email,
    store_otp_for_user,
)


@transaction.atomic
def register_vendor_service(data):
    if data.password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    if email_exists(data.email):
        raise HttpError(400, "This email is already registered")

    if phone_exists(data.phone):
        raise HttpError(400, "This phone number is already registered")

    if data.business_registration_number and business_number_exists(
        data.business_registration_number
    ):
        raise HttpError(
            400,
            "This business registration number is already in use",
        )

    user = None

    try:
        user = create_vendor_user(data)

        otp = generate_otp()
        store_otp_for_user(user, otp, minutes=10)
        send_or_log_otp_email(user, otp, data.email)

        refresh = RefreshToken.for_user(user)

        response = {
            "message": "Vendor registration successful! Please check your email for a verification code (OTP).",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "phone": user.phone,
                "email_verified": user.email_verified,
            },
            "vendor_profile": {
                "business_name": data.business_name,
                "business_registration_number": data.business_registration_number,
                "years_in_operation": data.years_in_operation,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }

        if settings.DEBUG:
            response["dev_otp"] = otp
            response["dev_message"] = "(Development mode — use this OTP to verify)"

        return response

    except Exception as e:
        if user is not None:
            delete_user(user)
        raise HttpError(400, f"Registration failed: {str(e)}")
