# permissions.py
from ninja.errors import HttpError


def corper_required(func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            raise HttpError(401, "Authentication required")
            
        if request.user.role != "corper":
            raise HttpError(403, "Only corpers are allowed here")
            
        return func(request, *args, **kwargs)
    
    # Preserve function metadata (good practice)
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    
    return wrapper


def vendor_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise HttpError(401, "Authentication required")
            
        if request.user.role != "vendor":
            raise HttpError(403, "Only vendors are allowed here")
            
        return func(request, *args, **kwargs)
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper