import time
from datetime import datetime, timedelta

import jwt
import pytest
from django.conf import settings

from modules.authenticator.utils.token import (
    generate_password_reset_token,
    verify_password_reset_token,
)


@pytest.mark.django_db
class TestPasswordResetToken:
    def test_generate_token_returns_string(self):
        token = generate_password_reset_token("1234")
        assert isinstance(token, str), "Token should be a string"

    def test_verify_token_returns_user_id(self):
        user_id = "abcd-1234"
        token = generate_password_reset_token(user_id)
        result, error = verify_password_reset_token(token)
        assert error is None
        assert result == user_id

    def test_invalid_token_returns_error(self):
        invalid_token = "this.is.not.a.token"
        result, error = verify_password_reset_token(invalid_token)
        assert result is None
        assert error == "Invalid token"

    def test_token_type_mismatch_returns_error(self):
        # Create a token with wrong type
        payload = {
            "user_id": "1234",
            "exp": datetime.utcnow() + timedelta(minutes=10),
            "type": "wrong_type",
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        result, error = verify_password_reset_token(token)
        assert result is None
        assert error == "Invalid token type"

    def test_expired_token_returns_error(self):
        # Generate token with 1 second expiry
        token = generate_password_reset_token(
            "1234", expires_minutes=0
        )  # 0 mins => expires immediately
        # Wait 1 second to ensure expiry

        time.sleep(1)
        result, error = verify_password_reset_token(token)
        assert result is None
        assert error == "Token has expired"
