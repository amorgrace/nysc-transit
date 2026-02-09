import pytest
from django.test import override_settings
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.schema import LoginSchema, LogoutSchema, VerifyOTPSchema
from modules.authenticator.services.auth_service import (
    login_service,
    logout_service,
    verify_otp_service,
)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_service_success(USER):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        email_verified=True,
    )

    data = LoginSchema(email="testuser@example.com", password="Password1!")
    resp = login_service(data)

    assert resp["message"] == "Login successful"
    assert resp["user"]["email"] == "testuser@example.com"
    assert resp["user"]["role"] == "corper"
    assert resp["user"]["email_verified"] is True
    assert "tokens" in resp
    assert "access" in resp["tokens"]
    assert "refresh" in resp["tokens"]


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_service_invalid_email(USER):
    data = LoginSchema(email="nonexistent@example.com", password="Password1!")

    with pytest.raises(HttpError) as exc_info:
        login_service(data)

    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_service_invalid_password(USER):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    data = LoginSchema(email="testuser@example.com", password="WrongPassword!")

    with pytest.raises(HttpError) as exc_info:
        login_service(data)

    assert exc_info.value.status_code == 401
    assert "Invalid email or password" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_service_inactive_user(USER):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=False,
    )

    data = LoginSchema(email="testuser@example.com", password="Password1!")

    with pytest.raises(HttpError) as exc_info:
        login_service(data)

    assert exc_info.value.status_code == 403
    assert "Account is inactive" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_logout_service_success(USER):
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )
    refresh = RefreshToken.for_user(user)
    data = LogoutSchema(refresh=str(refresh))

    resp = logout_service(data)
    assert resp["message"] == "Logged out successfully"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_logout_service_invalid_token(USER):
    data = LogoutSchema(refresh="invalid_token_string")

    with pytest.raises(HttpError) as exc_info:
        logout_service(data)

    assert exc_info.value.status_code == 400
    assert "Invalid or expired refresh token" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_logout_service_already_blacklisted(USER):
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )
    refresh = RefreshToken.for_user(user)
    refresh.blacklist()
    data = LogoutSchema(refresh=str(refresh))

    with pytest.raises(HttpError) as exc_info:
        logout_service(data)

    assert exc_info.value.status_code == 400


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_verify_otp_service_success(USER, monkeypatch):
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=False,
    )

    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: user,
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.verify_otp",
        lambda u, otp: (True, "OTP verified successfully"),
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.activate_user",
        lambda u: u.is_active or setattr(u, "is_active", True),
    )

    data = VerifyOTPSchema(email="testuser@example.com", otp="123456")
    resp = verify_otp_service(data)

    assert resp["success"] is True
    assert resp["message"] == "OTP verified successfully"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_verify_otp_service_user_not_found(USER, monkeypatch):
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: None,
    )

    data = VerifyOTPSchema(email="nonexistent@example.com", otp="123456")
    with pytest.raises(HttpError) as exc_info:
        verify_otp_service(data)

    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_verify_otp_service_invalid_otp(USER, monkeypatch):
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=False,
    )

    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: user,
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.verify_otp",
        lambda u, otp: (False, "Invalid or expired OTP"),
    )

    data = VerifyOTPSchema(email="testuser@example.com", otp="wrong_otp")
    with pytest.raises(HttpError) as exc_info:
        verify_otp_service(data)

    assert exc_info.value.status_code == 400
    assert "Invalid or expired OTP" in str(exc_info.value)
