from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


def get_user_by_email(email: str):
    return User.objects.filter(email=email).first()


def activate_user(user):
    user.is_active = True
    user.save(update_fields=["is_active"])


def update_user_password(user, new_password):
    user.password = make_password(new_password)
    user.save(update_fields=["password"])
