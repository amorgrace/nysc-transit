# permissions.py
from functools import wraps

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from ninja.errors import HttpError
from ninja.security import HttpBearer

User = get_user_model()


def corper_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, "user") or not request.user.is_authenticated:
            raise HttpError(401, "Authentication required")

        if request.user.role != "corper":
            raise HttpError(403, "Only corpers are allowed here")

        return func(request, *args, **kwargs)

    return wrapper


def vendor_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise HttpError(401, "Authentication required")

        if request.user.role != "vendor":
            raise HttpError(403, "Only vendors are allowed here")

        return func(request, *args, **kwargs)

    return wrapper


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if not user_id:
                return None
            try:
                user = User.objects.get(id=user_id)
                return user
            except User.DoesNotExist:
                return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
