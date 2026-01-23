# permissions.py
from functools import wraps

from ninja.errors import HttpError


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
