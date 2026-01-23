from datetime import date

import pytest
from django.test import override_settings
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.schema import (
    CorperSignupSchema,
    LoginSchema,
    LogoutSchema,
    VendorSignupSchema,
    VerifyOTPSchema,
)
from modules.authenticator.views import (
    login,
    logout,
    register_corper,
    register_vendor,
    verify_otp_endpoint,
)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_register_corper_and_verify_flow(USER, monkeypatch):
    data = CorperSignupSchema(
        username=None,
        email="testcorper@example.com",
        password="Password1!",
        confirm_password="Password1!",
        full_name="Test Corper",
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )

    orig_create = USER.objects.create_user

    def _create_user(email, password=None, **extra):
        extra.pop("username", None)
        return orig_create(email=email, password=password, **extra)

    monkeypatch.setattr(
        "modules.authenticator.views.User.objects.create_user", _create_user
    )

    resp = register_corper(object(), data)
    assert resp["user"]["email"] == "testcorper@example.com"
    assert "dev_otp" in resp

    user = USER.objects.get(email="testcorper@example.com")
    assert user.is_active is False

    otp = resp["dev_otp"]
    verify_data = VerifyOTPSchema(email="testcorper@example.com", otp=otp)
    verify_resp = verify_otp_endpoint(object(), verify_data)
    assert verify_resp["success"] is True
    # user should now be active
    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_register_vendor(USER, monkeypatch):
    data = VendorSignupSchema(
        username=None,
        email="vendor@example.com",
        password="Password1!",
        confirm_password="Password1!",
        phone="07012345678",
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )

    orig_create = USER.objects.create_user

    def _create_user(email, password=None, **extra):
        extra.pop("username", None)
        return orig_create(email=email, password=password, **extra)

    monkeypatch.setattr(
        "modules.authenticator.views.User.objects.create_user", _create_user
    )

    resp = register_vendor(object(), data)
    assert resp["user"]["email"] == "vendor@example.com"
    assert resp["user"]["role"] == "vendor"
    assert "dev_otp" in resp


# test for login


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_success(USER):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    data = LoginSchema(
        email="testuser@example.com",
        password="Password1!",
    )

    resp = login(object(), data)
    assert resp["message"] == "Login successful"
    assert resp["user"]["email"] == "testuser@example.com"
    assert "tokens" in resp
    assert "access" in resp["tokens"]
    assert "refresh" in resp["tokens"]


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_invalid_credentials(USER):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    data = LoginSchema(
        email="testuser@example.com",
        password="WrongPassword!",
    )

    with pytest.raises(HttpError) as exc_info:
        login(object(), data)
    assert exc_info.value.status_code == 401


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_inactive_user(USER):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=False,
    )

    data = LoginSchema(
        email="testuser@example.com",
        password="Password1!",
    )

    with pytest.raises(HttpError) as exc_info:
        login(object(), data)
    assert exc_info.value.status_code == 403


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_login_user_not_found(USER):
    data = LoginSchema(
        email="nonexistent@example.com",
        password="Password1!",
    )

    with pytest.raises(HttpError) as exc_info:
        login(object(), data)
    assert exc_info.value.status_code == 401


# test for logout


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_logout_success(USER):
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    refresh = RefreshToken.for_user(user)

    data = LogoutSchema(refresh=str(refresh))

    resp = logout(object(), data)
    assert resp["message"] == "Logged out successfully"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_logout_invalid_token(USER):
    data = LogoutSchema(refresh="invalid_token_string")

    with pytest.raises(HttpError) as exc_info:
        logout(object(), data)
    assert exc_info.value.status_code == 400
