from typing import cast

from django.contrib.auth import get_user_model

from modules.authenticator.models import User as CustomUser
from modules.vendor.models import Vendor as VendorProfile

User = get_user_model()


def email_exists(email: str) -> bool:
    return User.objects.filter(email=email).exists()


def phone_exists(phone: str) -> bool:
    return User.objects.filter(phone=phone).exists()


def business_number_exists(business_registration_number: str) -> bool:
    return VendorProfile.objects.filter(
        business_registration_number=business_registration_number
    ).exists()


def create_vendor_user(data) -> CustomUser:
    user = cast(
        CustomUser,
        User.objects.create_user(
            email=data.email,
            password=data.password,
            full_name=data.business_name,
            phone=data.phone,
            role=User.Role.VENDOR,
            is_active=False,
            email_verified=False,
        ),
    )

    VendorProfile.objects.create(
        user=user,
        phone=data.phone,
        business_name=data.business_name,
        business_registration_number=data.business_registration_number or "",
        years_in_operation=data.years_in_operation,
    )

    return user


def delete_user(user):
    user.delete()
