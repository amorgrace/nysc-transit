from typing import cast

from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.errors import HttpError
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.crud.user_crud import (
    activate_user,
    get_user_by_email,
    update_user_password,
)
from modules.authenticator.models import User as CustomUser
from modules.authenticator.utils.email import (
    generate_otp,
    send_or_log_otp_email,
    store_otp_for_user,
    verify_otp,
)
from modules.authenticator.utils.token import (
    generate_password_reset_token,
    verify_password_reset_token,
)

User = get_user_model()


def login_service(data):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        raise HttpError(401, "Invalid email or password")

    if not user.check_password(data.password):
        raise HttpError(401, "Invalid email or password")

    if not user.is_active:
        raise HttpError(403, "Account is inactive. Please contact support.")

    user = cast(CustomUser, user)

    refresh = RefreshToken.for_user(user)

    return {
        "message": "Login successful",
        "user": {
            "email": user.email,
            "role": user.role,
            "email_verified": user.email_verified,
        },
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        },
    }


def logout_service(data):
    try:
        refresh_token = RefreshToken(data.refresh)
        refresh_token.blacklist()

        return {"message": "Logged out successfully"}

    except TokenError:
        raise HttpError(400, "Invalid or expired refresh token")
    except Exception as e:
        raise HttpError(400, f"Logout failed: {str(e)}")


def verify_otp_service(data):
    user = get_user_by_email(data.email)

    if not user:
        raise HttpError(404, "User not found")

    success, message = verify_otp(user, data.otp)

    if not success:
        raise HttpError(400, message)

    activate_user(user)

    return {
        "message": message,
        "success": True,
    }


def resend_otp_service(data):
    user = get_user_by_email(data.email)

    if not user:
        raise HttpError(404, "User not found")

    if user.is_active:
        raise HttpError(400, "User already verified")

    otp = generate_otp()
    store_otp_for_user(user, otp)
    send_or_log_otp_email(user, otp, user.email)

    response = {
        "success": True,
        "message": "OTP resent successfully",
    }

    if settings.DEBUG:
        response["otp"] = otp

    return response


def forgot_password_service(data):
    user = get_user_by_email(data.email)

    # Always return success to prevent email enumeration
    if not user:
        return {
            "success": True,
            "message": "If your email exists, a reset link has been sent",
        }

    token = generate_password_reset_token(user.id)
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    send_or_log_otp_email(
        None,
        user.email,
        f"Click this link to reset your password: {reset_link}",
    )

    response = {
        "success": True,
        "message": "If your email exists, a reset link has been sent",
    }

    # Expose token in DEBUG for dev convenience
    if settings.DEBUG:
        response["token"] = token

    return response


def reset_password_service(data):
    if data.new_password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    user_id, error = verify_password_reset_token(data.token)
    if error:
        raise HttpError(400, error)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")

    update_user_password(user, data.new_password)

    return {"success": True, "message": "Password reset successfully"}
