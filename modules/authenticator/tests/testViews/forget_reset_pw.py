from datetime import datetime, timedelta

import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password

from modules.authenticator.schema import ForgotPasswordSchema, ResetPasswordSchema
from modules.authenticator.utils.token import (
    generate_password_reset_token,
    verify_password_reset_token,
)
from modules.authenticator.views import forgot_password, reset_password

VALID_PASSWORD = "Password@123"
NEW_PASSWORD = "NewPassword@456"

User = get_user_model()


# Tests for forgot_password endpoint


@pytest.mark.django_db
def test_forgot_password_existing_user(USER):
    """Test forgot password for existing user"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        full_name="Test User",
        is_active=True,
    )

    data = ForgotPasswordSchema(email="test@example.com")
    resp = forgot_password(object(), data)

    assert resp["success"] is True
    assert resp["message"] == "If your email exists, a reset link has been sent"
    assert "token" in resp
    assert len(resp["token"]) > 0

    # Verify the token is valid
    user_id, error = verify_password_reset_token(resp["token"])
    assert error is None
    assert user_id == str(user.id)


@pytest.mark.django_db
def test_forgot_password_nonexistent_user(USER):
    """Test forgot password for non-existent user (should still return success)"""
    data = ForgotPasswordSchema(email="nonexistent@example.com")
    resp = forgot_password(object(), data)

    # Should return success to avoid email enumeration
    assert resp["success"] is True
    assert resp["message"] == "If your email exists, a reset link has been sent"


@pytest.mark.django_db
def test_forgot_password_generates_valid_token(USER):
    """Test that forgot password generates a valid JWT token"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
    )

    data = ForgotPasswordSchema(email="test@example.com")
    resp = forgot_password(object(), data)

    token = resp["token"]

    # Decode and verify token payload
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["user_id"] == str(user.id)
    assert payload["type"] == "password_reset"
    assert "exp" in payload


@pytest.mark.django_db
def test_forgot_password_inactive_user(USER):
    """Test forgot password for inactive user"""
    user = USER.objects.create_user(
        email="inactive@example.com",
        password=VALID_PASSWORD,
        is_active=False,
    )

    data = ForgotPasswordSchema(email="inactive@example.com")
    resp = forgot_password(object(), data)

    assert resp["success"] is True
    assert "token" in resp

    # Token should still be valid even for inactive users
    user_id, error = verify_password_reset_token(resp["token"])
    assert error is None
    assert user_id == str(user.id)


# Tests for reset_password endpoint


@pytest.mark.django_db
def test_reset_password_success(USER):
    """Test successful password reset"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
    )

    token = generate_password_reset_token(user.id)

    data = ResetPasswordSchema(
        token=token, new_password=NEW_PASSWORD, confirm_password=NEW_PASSWORD
    )
    resp = reset_password(object(), data)

    assert resp["success"] is True
    assert resp["message"] == "Password reset successfully"

    # Verify password was changed
    user.refresh_from_db()
    assert check_password(NEW_PASSWORD, user.password)
    assert not check_password(VALID_PASSWORD, user.password)


@pytest.mark.django_db
def test_reset_password_mismatched_passwords(USER):
    """Test reset password with mismatched passwords"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
    )

    token = generate_password_reset_token(user.id)

    data = ResetPasswordSchema(
        token=token, new_password=NEW_PASSWORD, confirm_password="DifferentPassword@789"
    )

    with pytest.raises(Exception) as exc_info:
        reset_password(object(), data)

    assert exc_info.value.status_code == 400
    assert "Passwords do not match" in str(exc_info.value)

    # Verify password was NOT changed
    user.refresh_from_db()
    assert check_password(VALID_PASSWORD, user.password)


@pytest.mark.django_db
def test_reset_password_invalid_token(USER):
    """Test reset password with invalid token"""
    USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
    )

    data = ResetPasswordSchema(
        token="invalid_token_12345",
        new_password=NEW_PASSWORD,
        confirm_password=NEW_PASSWORD,
    )

    with pytest.raises(Exception) as exc_info:
        reset_password(object(), data)

    assert exc_info.value.status_code == 400
    assert "Invalid token" in str(exc_info.value)


@pytest.mark.django_db
def test_reset_password_expired_token(USER):
    """Test reset password with expired token"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
    )

    # Generate token that expires immediately
    token = generate_password_reset_token(user.id, expires_minutes=-1)

    data = ResetPasswordSchema(
        token=token, new_password=NEW_PASSWORD, confirm_password=NEW_PASSWORD
    )

    with pytest.raises(Exception) as exc_info:
        reset_password(object(), data)

    assert exc_info.value.status_code == 400
    assert "Token has expired" in str(exc_info.value)

    # Verify password was NOT changed
    user.refresh_from_db()
    assert check_password(VALID_PASSWORD, user.password)


@pytest.mark.django_db
def test_reset_password_user_not_found(USER):
    """Test reset password when user no longer exists"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
    )

    token = generate_password_reset_token(user.id)
    user.delete()

    data = ResetPasswordSchema(
        token=token, new_password=NEW_PASSWORD, confirm_password=NEW_PASSWORD
    )

    with pytest.raises(Exception) as exc_info:
        reset_password(object(), data)

    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value)


@pytest.mark.django_db
def test_reset_password_wrong_token_type(USER):
    """Test reset password with wrong token type"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
    )

    # Generate a token with wrong type
    payload = {
        "user_id": str(user.id),
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "type": "email_verification",  # Wrong type
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    data = ResetPasswordSchema(
        token=token, new_password=NEW_PASSWORD, confirm_password=NEW_PASSWORD
    )

    with pytest.raises(Exception) as exc_info:
        reset_password(object(), data)

    assert exc_info.value.status_code == 400
    assert "Invalid token type" in str(exc_info.value)


@pytest.mark.django_db
def test_reset_password_updates_only_password(USER):
    """Test that reset password only updates the password field"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        full_name="Original Name",
        is_active=True,
        email_verified=True,
    )

    original_email = user.email
    original_name = user.full_name
    original_active = user.is_active

    token = generate_password_reset_token(user.id)

    data = ResetPasswordSchema(
        token=token, new_password=NEW_PASSWORD, confirm_password=NEW_PASSWORD
    )
    reset_password(object(), data)

    user.refresh_from_db()

    # Verify only password changed
    assert check_password(NEW_PASSWORD, user.password)
    assert user.email == original_email
    assert user.full_name == original_name
    assert user.is_active == original_active


# Tests for token utility functions


def test_generate_password_reset_token(USER):
    """Test generating password reset token"""
    user_id = "test-user-id-123"
    token = generate_password_reset_token(user_id)

    assert token is not None
    assert len(token) > 0

    # Verify token can be decoded
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["user_id"] == user_id
    assert payload["type"] == "password_reset"


def test_verify_password_reset_token_valid():
    """Test verifying valid password reset token"""
    user_id = "test-user-id-123"
    token = generate_password_reset_token(user_id)

    verified_user_id, error = verify_password_reset_token(token)

    assert error is None
    assert verified_user_id == user_id


def test_verify_password_reset_token_expired():
    """Test verifying expired token"""
    user_id = "test-user-id-123"
    token = generate_password_reset_token(user_id, expires_minutes=-1)

    verified_user_id, error = verify_password_reset_token(token)

    assert verified_user_id is None
    assert error == "Token has expired"


def test_verify_password_reset_token_invalid():
    """Test verifying invalid token"""
    verified_user_id, error = verify_password_reset_token("invalid_token")

    assert verified_user_id is None
    assert error == "Invalid token"


def test_verify_password_reset_token_wrong_type():
    """Test verifying token with wrong type"""
    payload = {
        "user_id": "test-user-id-123",
        "exp": datetime.utcnow() + timedelta(minutes=30),
        "type": "access_token",  # Wrong type
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    verified_user_id, error = verify_password_reset_token(token)

    assert verified_user_id is None
    assert error == "Invalid token type"
