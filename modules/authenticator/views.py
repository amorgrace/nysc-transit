from django.contrib.auth import get_user_model
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from modules.authenticator.services.auth_service import (
    forgot_password_service,
    login_service,
    logout_service,
    resend_otp_service,
    reset_password_service,
    verify_otp_service,
)
from modules.authenticator.services.corper_service import register_corper_service
from modules.authenticator.services.user_service import get_current_user_service
from modules.authenticator.services.vendor_service import register_vendor_service

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

router = Router(tags=["Auth"])

User = get_user_model()
jwt_auth = JWTAuth()


@router.post("/corper/register", auth=None)
def register_corper(request, data: CorperSignupSchema):
    return register_corper_service(data)


@router.post("/vendor/register", auth=None)
def register_vendor(request, data: VendorSignupSchema):
    return register_vendor_service(data)


@router.post("/login", auth=None)
def login(request, data: LoginSchema):
    return login_service(data)


@router.post("/logout", auth=None)
def logout(request, data: LogoutSchema):
    return logout_service(data)


@router.post("/verify-otp", auth=None)
def verify_otp_endpoint(request, data: VerifyOTPSchema):
    return verify_otp_service(data)


@router.post("/resend-otp", auth=None)
def resend_otp_endpoint(request, data: ResendOTPSchema):
    return resend_otp_service(data)


@router.get("/user/me", response=UserOutSchema, auth=jwt_auth)
def get_current_user(request):
    return get_current_user_service(request.auth)


@router.post("/forgot-password", auth=None)
def forgot_password(request, data: ForgotPasswordSchema):
    return forgot_password_service(data)


@router.post("/reset-password", auth=None)
def reset_password(request, data: ResetPasswordSchema):
    return reset_password_service(data)
