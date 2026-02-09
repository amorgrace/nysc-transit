from django.conf import settings
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.crud.corper_crud import (
    create_corper_user,
    delete_user,
    email_exists,
)
from modules.authenticator.utils.email import (
    generate_otp,
    send_or_log_otp_email,
    store_otp_for_user,
)


def register_corper_service(data):
    if data.password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    if email_exists(data.email):
        raise HttpError(400, "This email is already registered")

    user = None

    try:
        user = create_corper_user(data)

        otp = generate_otp()
        store_otp_for_user(user, otp, minutes=10)
        send_or_log_otp_email(user, otp, data.email)

        refresh = RefreshToken.for_user(user)

        response = {
            "message": "Registration successful! Please verify your email.",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "email_verified": user.email_verified,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
        }

        if settings.DEBUG:
            response["dev_otp"] = otp
            response["dev_message"] = "Development mode: Use this OTP to verify"

        return response

    except Exception as e:
        if user is not None:
            delete_user(user)
        raise HttpError(400, f"Registration failed: {str(e)}")
