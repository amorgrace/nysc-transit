from typing import cast

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import TokenError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.models import User as CustomUser
from modules.corper.models import CorperProfile
from modules.corper.schemas import CorperProfileOut
from modules.vendor.models import VendorProfile
from modules.vendor.schemas import VendorProfileOut

from .schema import (
    CorperSignupSchema,
    ForgotPasswordSchema,
    LoginSchema,
    LogoutSchema,
    ResendOTPSchema,
    ResetPasswordSchema,
    UserOutSchema,
    VendorSignupSchema,
    VerifyOTPSchema,
)
from .utils.email import (
    generate_otp,
    send_or_log_otp_email,
    store_otp_for_user,
    verify_otp,
)
from .utils.token import generate_password_reset_token, verify_password_reset_token

router = Router(tags=["Auth"])

User = get_user_model()
jwt_auth = JWTAuth()


@router.post("/corper/register", auth=None)
def register_corper(request, data: CorperSignupSchema):
    if data.password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    # Your existing uniqueness checks...
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "This email is already registered")
    # ... other checks ...

    user = None
    try:
        user = cast(
            CustomUser,
            User.objects.create_user(
                email=data.email,
                password=data.password,
                full_name=data.full_name,
                role=User.Role.CORPER,  # type: ignore
                is_active=False,  # ← you can keep True or set False until verified
                phone=data.phone,
                # username=data.username or data.email,
            ),
        )

        CorperProfile.objects.create(
            user=user,
            phone=data.phone,
            state_code=data.state_code,
            call_up_number=data.call_up_number,
            deployment_state=data.deployment_state,
            camp_location=data.camp_location,
            deployment_date=data.deployment_date,
        )

        # Generate & store OTP
        otp = generate_otp()
        store_otp_for_user(user, otp, minutes=10)

        # "Send" (or log) email
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
            "corper_profile": {
                # ... your fields ...
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),  # type: ignore
            },
        }

        # DEV MODE: expose OTP so frontend can show it
        if settings.DEBUG:
            response["dev_otp"] = otp
            response["dev_message"] = "Development mode: Use this OTP to verify"

        return response

    except Exception as e:
        if user is not None:
            user.delete()
        raise HttpError(400, f"Registration failed: {str(e)}")


@router.post("/vendor/register", auth=None)
def register_vendor(request, data: VendorSignupSchema):
    """
    Register a new Vendor — starts inactive, requires OTP verification
    """
    # 1. Basic validation
    if data.password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    # 2. Uniqueness checks
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "This email is already registered")

    if User.objects.filter(phone=data.phone).exists():
        raise HttpError(400, "This phone number is already registered")

    if (
        data.business_registration_number
        and VendorProfile.objects.filter(
            business_registration_number=data.business_registration_number
        ).exists()
    ):
        raise HttpError(400, "This business registration number is already in use")

    user = None
    try:
        # 3. Create base user — INACTIVE until verified
        user = cast(
            CustomUser,
            User.objects.create_user(
                email=data.email,
                password=data.password,
                full_name=data.business_name,  # business name as display name
                phone=data.phone,
                role=User.Role.VENDOR,  # type: ignore
                is_active=False,  # ← key change
                email_verified=False,
                # username=data.username or data.email,
            ),
        )

        # 4. Create VendorProfile
        VendorProfile.objects.create(
            user=user,
            business_name=data.business_name,
            business_registration_number=data.business_registration_number or "",
            years_in_operation=data.years_in_operation,
            description=data.description or "",
        )

        # 5. Generate & store OTP
        otp = generate_otp()
        store_otp_for_user(user, otp, minutes=10)

        # 6. "Send" OTP (logs to console in dev, real send in prod)
        send_or_log_otp_email(user, otp, data.email)

        # 7. Generate tokens anyway (frontend can store them, but login will fail until verified)
        refresh = RefreshToken.for_user(user)

        # 8. Response
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
                "description": data.description,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),  # type: ignore
            },
        }

        # Dev convenience: expose OTP in response
        if settings.DEBUG:
            response["dev_otp"] = otp
            response["dev_message"] = "(Development mode — use this OTP to verify)"

        return response

    except Exception as e:
        if user is not None:
            user.delete()
        raise HttpError(400, f"Registration failed: {str(e)}")


@router.post("/login", auth=None)
def login(request, data: LoginSchema):
    """
    Login user and return JWT tokens
    """
    try:
        user = User.objects.get(email=data.email)
        if not user.check_password(data.password):
            raise HttpError(401, "Invalid email or password")
        if not user.is_active:
            raise HttpError(403, "Account is inactive. Please contact support.")
    except User.DoesNotExist:
        raise HttpError(401, "Invalid email or password")

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


@router.post("/logout", auth=None)  # auth=None because we check token manually
def logout(request, data: LogoutSchema):
    """
    Blacklist the refresh token to log the user out
    """
    try:
        # Validate and blacklist the refresh token
        refresh_token = RefreshToken(data.refresh)  # type: ignore
        refresh_token.blacklist()  # This marks it as unusable

        return {"message": "Logged out successfully"}

    except TokenError:
        raise HttpError(400, "Invalid or expired refresh token")
    except Exception as e:
        raise HttpError(400, f"Logout failed: {str(e)}")


@router.post("/verify-otp", auth=None)
def verify_otp_endpoint(request, data: VerifyOTPSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")

    success, message = verify_otp(user, data.otp)
    if success:
        user.is_active = True
        user.save(update_fields=["is_active"])
        return {"message": message, "success": True}
    else:
        raise HttpError(400, message)


@router.post("/resend-otp", auth=None)
def resend_otp_endpoint(request, data: ResendOTPSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")

    if user.is_active:
        raise HttpError(400, "User already verified")

    otp = generate_otp()
    store_otp_for_user(user, otp)
    send_or_log_otp_email(request, otp, user.email)

    return {"success": True, "message": "OTP resent successfully", "otp": otp}


@router.get("/user/me", response=UserOutSchema, auth=jwt_auth)
def get_current_user(request):
    user = request.auth
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
                business_name=vendor.business_name,
                business_registration_number=vendor.business_registration_number,
                years_in_operation=vendor.years_in_operation,
                description=vendor.description,
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


@router.post("/forgot-password", auth=None)
def forgot_password(request, data: ForgotPasswordSchema):
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        # Always return success to avoid email enumeration
        return {
            "success": True,
            "message": "If your email exists, a reset link has been sent",
        }

    token = generate_password_reset_token(user.id)

    # Send token via email
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    send_or_log_otp_email(
        request, user.email, f"Click this link to reset your password: {reset_link}"
    )

    return {
        "success": True,
        "token": token,
        "message": "If your email exists, a reset link has been sent",
    }


@router.post("/reset-password", auth=None)
def reset_password(request, data: ResetPasswordSchema):
    if data.new_password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    user_id, error = verify_password_reset_token(data.token)
    if error:
        raise HttpError(400, error)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")

    user.password = make_password(data.new_password)
    user.save(update_fields=["password"])

    return {"success": True, "message": "Password reset successfully"}
