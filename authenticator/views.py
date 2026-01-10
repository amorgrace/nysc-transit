# authenticator/views.py
from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth import get_user_model
from ninja_jwt.tokens import RefreshToken
from django.conf import settings
from vendor.models import VendorProfile
from .schema import *
from ninja_jwt.exceptions import TokenError
from django.contrib.auth import authenticate
from corper.models import CorperProfile


router = Router(tags=["Auth"])

User = get_user_model()


@router.post("/corper/register", auth=None)
def register_corper(request, data: CorperSignupSchema):
    """
    Register a new NYSC Corper with profile creation
    """
    # 1. Password match check
    if data.password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    # 2. Uniqueness checks (prevent duplicates)
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "This email is already registered")

    if CorperProfile.objects.filter(phone=data.phone).exists():
        raise HttpError(400, "This phone number is already registered")

    if CorperProfile.objects.filter(state_code=data.state_code).exists():
        raise HttpError(400, "This state code is already registered")

    if CorperProfile.objects.filter(call_up_number=data.call_up_number).exists():
        raise HttpError(400, "This call-up number is already in use")

    try:
        # 3. Create the base user
        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            full_name=data.full_name,             
            role=User.Role.CORPER,
            is_active=True,
            phone=data.phone,
        )

        # 4. Create the CorperProfile immediately (matches your exact model)
        CorperProfile.objects.create(
            user=user,
            phone=data.phone,
            state_code=data.state_code,
            call_up_number=data.call_up_number,
            deployment_state=data.deployment_state,
            camp_location=data.camp_location,
            deployment_date=data.deployment_date,
        )

        # 5. Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # 6. Success response
        return {
            "message": "Corper registration successful! Welcome to NYSC service.",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,

            },
            "corper_profile": {
                "phone": user.phone,
                "state_code": data.state_code,
                "call_up_number": data.call_up_number,
                "deployment_state": data.deployment_state,
                "camp_location": data.camp_location,
                "deployment_date": data.deployment_date.strftime("%Y-%m-%d"),
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }

    except Exception as e:
        # Clean up if something fails (optional but good practice)
        if 'user' in locals():
            user.delete()
        raise HttpError(400, f"Registration failed: {str(e)}")



@router.post("/vendor/register", auth=None)
def register_vendor(request, data: VendorSignupSchema):
    """
    Register a new Vendor
    """
    # 1. Basic validation
    if data.password != data.confirm_password:
        raise HttpError(400, "Passwords do not match")

    # 2. Uniqueness checks
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "This email is already registered")

    if User.objects.filter(phone=data.phone).exists():
        raise HttpError(400, "This phone number is already registered")

    # Optional: check business registration number if you want it unique
    if data.business_registration_number and VendorProfile.objects.filter(
        business_registration_number=data.business_registration_number
    ).exists():
        raise HttpError(400, "This business registration number is already in use")

    try:
        # 3. Create base user
        user = User.objects.create_user(
            email=data.email,
            password=data.password,
            full_name=data.business_name,     # using business name as display name
            phone=data.phone,
            role=User.Role.VENDOR,
            is_active=True,                   # ← change to False later if verification needed
        )

        # 4. Create VendorProfile
        VendorProfile.objects.create(
            user=user,
            business_name=data.business_name,
            business_registration_number=data.business_registration_number or "",
            years_in_operation=data.years_in_operation,
            description=data.description or "",
        )

        # 5. Generate tokens
        refresh = RefreshToken.for_user(user)

        # 6. Response
        return {
            "message": "Vendor registration successful!",
            "user": {
                "email": user.email,
                "full_name": user.full_name,      # which is business_name
                "role": user.role,
                "phone": user.phone,
            },
            "vendor_profile": {
                "business_name": data.business_name,
                "business_registration_number": data.business_registration_number,
                "years_in_operation": data.years_in_operation,
                "description": data.description,
            },
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }

    except Exception as e:
        if 'user' in locals():
            user.delete()
        raise HttpError(400, f"Registration failed: {str(e)}")
    


@router.post("/login", auth=None)
def login(request, data: LoginSchema):
    """
    Login user and return JWT tokens
    """
    user = authenticate(request, email=data.email, password=data.password)

    if user is None:
        raise HttpError(401, "Invalid email or password")

    if not user.is_active:
        raise HttpError(403, "Account is inactive. Please contact support.")

    refresh = RefreshToken.for_user(user)

    return {
        "message": "Login successful",
        "user": {
            "email": user.email,
            "role": user.role,
        },
        "tokens": {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
    }


@router.post("/logout", auth=None)  # auth=None because we check token manually
def logout(request, data: LogoutSchema):
    """
    Blacklist the refresh token to log the user out
    """
    try:
        # Validate and blacklist the refresh token
        refresh_token = RefreshToken(data.refresh)
        refresh_token.blacklist()  # This marks it as unusable

        return {
            "message": "Logged out successfully"
        }

    except TokenError:
        raise HttpError(400, "Invalid or expired refresh token")
    except Exception as e:
        raise HttpError(400, f"Logout failed: {str(e)}")