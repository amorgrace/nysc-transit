from typing import cast

from django.contrib.auth import get_user_model

from modules.authenticator.models import User as CustomUser
from modules.corper.models import CorperProfile

User = get_user_model()


def email_exists(email: str) -> bool:
    return User.objects.filter(email=email).exists()


def create_corper_user(data) -> CustomUser:
    user = cast(
        CustomUser,
        User.objects.create_user(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            role=User.Role.CORPER,
            is_active=False,
            phone=data.phone,
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

    return user


def delete_user(user):
    user.delete()
