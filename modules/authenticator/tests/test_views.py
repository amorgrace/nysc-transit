from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.test import override_settings
from django.utils import timezone

from modules.authenticator.schema import (
    CorperSignupSchema,
    VendorSignupSchema,
    VerifyOTPSchema,
)
from modules.authenticator.views import (
    register_corper,
    register_vendor,
    verify_otp_endpoint,
)

VALID_PASSWORD = "Password@123"

User = get_user_model()


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


# New tests for verify_otp_endpoint


@pytest.mark.django_db
def test_verify_otp_success(USER):
    """Test successful OTP verification"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=False,
        otp_code="123456",
        otp_expires_at=timezone.now() + timezone.timedelta(minutes=10),
    )

    verify_data = VerifyOTPSchema(email="test@example.com", otp="123456")
    resp = verify_otp_endpoint(object(), verify_data)

    assert resp["success"] is True
    assert resp["message"] == "Email verified successfully!"

    user.refresh_from_db()
    assert user.is_active is True
    assert user.email_verified is True
    assert user.otp_code is None
    assert user.otp_expires_at is None


@pytest.mark.django_db
def test_verify_otp_user_not_found(USER):
    """Test verification with non-existent user"""
    verify_data = VerifyOTPSchema(email="nonexistent@example.com", otp="123456")

    with pytest.raises(Exception) as exc_info:
        verify_otp_endpoint(object(), verify_data)

    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value)


@pytest.mark.django_db
def test_verify_otp_invalid_code(USER):
    """Test verification with wrong OTP"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=False,
        otp_code="123456",
        otp_expires_at=timezone.now() + timezone.timedelta(minutes=10),
    )

    verify_data = VerifyOTPSchema(email="test@example.com", otp="wrong_otp")

    with pytest.raises(Exception) as exc_info:
        verify_otp_endpoint(object(), verify_data)

    assert exc_info.value.status_code == 400
    assert "Invalid OTP" in str(exc_info.value)

    user.refresh_from_db()
    assert user.is_active is False
    assert user.email_verified is False


@pytest.mark.django_db
def test_verify_otp_expired(USER):
    """Test verification with expired OTP"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=False,
        otp_code="123456",
        otp_expires_at=timezone.now() - timezone.timedelta(minutes=1),
    )

    verify_data = VerifyOTPSchema(email="test@example.com", otp="123456")

    with pytest.raises(Exception) as exc_info:
        verify_otp_endpoint(object(), verify_data)

    assert exc_info.value.status_code == 400
    assert "OTP has expired" in str(exc_info.value)

    user.refresh_from_db()
    assert user.is_active is False
    assert user.otp_code is None
    assert user.otp_expires_at is None


@pytest.mark.django_db
def test_verify_otp_no_otp_found(USER):
    """Test verification when user has no OTP"""
    USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=False,
        otp_code=None,
        otp_expires_at=None,
    )

    verify_data = VerifyOTPSchema(email="test@example.com", otp="123456")

    with pytest.raises(Exception) as exc_info:
        verify_otp_endpoint(object(), verify_data)

    assert exc_info.value.status_code == 400
    assert "No OTP found" in str(exc_info.value)


@pytest.mark.django_db
def test_verify_otp_already_active_user(USER):
    """Test verification for already active user with valid OTP"""
    user = USER.objects.create_user(
        email="test@example.com",
        password=VALID_PASSWORD,
        is_active=True,
        email_verified=True,
        otp_code="123456",
        otp_expires_at=timezone.now() + timezone.timedelta(minutes=10),
    )

    verify_data = VerifyOTPSchema(email="test@example.com", otp="123456")
    resp = verify_otp_endpoint(object(), verify_data)

    # Should still succeed and clean up OTP
    assert resp["success"] is True

    user.refresh_from_db()
    assert user.is_active is True
    assert user.otp_code is None
    assert user.otp_expires_at is None
