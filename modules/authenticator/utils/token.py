from datetime import datetime, timedelta

import jwt
from django.conf import settings


def generate_password_reset_token(user_id: str, expires_minutes=30):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=expires_minutes),
        "type": "password_reset",
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "password_reset":
            return None, "Invalid token type"
        return payload["user_id"], None
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"
