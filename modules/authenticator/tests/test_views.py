from datetime import date

import pytest
from django.test import override_settings
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.schema import (
    CorperSignupSchema,
    ForgotPasswordSchema,
    LoginSchema,
    LogoutSchema,
    ResendOTPSchema,
    ResetPasswordSchema,
    VendorSignupSchema,
    VerifyOTPSchema,
)
from modules.authenticator.views import (
    forgot_password,
    get_current_user,
    login,
    logout,
    register_corper,
    register_vendor,
    resend_otp_endpoint,
    reset_password,
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


#  tests for verify/resend/getuser/forget and reset pw


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_verify_otp_success(USER, monkeypatch):
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=False,
    )

    def mock_verify_otp(user, otp):
        return True, "OTP verified successfully"

    monkeypatch.setattr("modules.authenticator.views.verify_otp", mock_verify_otp)

    data = VerifyOTPSchema(email="testuser@example.com", otp="123456")

    resp = verify_otp_endpoint(object(), data)
    assert resp["success"] is True

    user.refresh_from_db()
    assert user.is_active is True


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_verify_otp_invalid(USER, monkeypatch):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=False,
    )

    def mock_verify_otp(user, otp):
        return False, "Invalid OTP"

    monkeypatch.setattr("modules.authenticator.views.verify_otp", mock_verify_otp)

    data = VerifyOTPSchema(email="testuser@example.com", otp="wrong")

    with pytest.raises(HttpError) as exc_info:
        verify_otp_endpoint(object(), data)
    assert exc_info.value.status_code == 400


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_verify_otp_user_not_found(USER):
    data = VerifyOTPSchema(email="nonexistent@example.com", otp="123456")

    with pytest.raises(HttpError) as exc_info:
        verify_otp_endpoint(object(), data)
    assert exc_info.value.status_code == 404


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_resend_otp_success(USER, monkeypatch):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=False,
    )

    def mock_generate_otp():
        return "123456"

    def mock_store_otp(user, otp):
        pass

    def mock_send_email(request, otp, email):
        pass

    monkeypatch.setattr("modules.authenticator.views.generate_otp", mock_generate_otp)
    monkeypatch.setattr(
        "modules.authenticator.views.store_otp_for_user", mock_store_otp
    )
    monkeypatch.setattr(
        "modules.authenticator.views.send_or_log_otp_email", mock_send_email
    )

    data = ResendOTPSchema(email="testuser@example.com")

    resp = resend_otp_endpoint(object(), data)
    assert resp["success"] is True
    assert resp["otp"] == "123456"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_resend_otp_already_verified(USER):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    data = ResendOTPSchema(email="testuser@example.com")

    with pytest.raises(HttpError) as exc_info:
        resend_otp_endpoint(object(), data)
    assert exc_info.value.status_code == 400


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_current_user_corper(USER):
    user = USER.objects.create_user(
        email="corper@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        full_name="Test Corper",
    )

    from modules.corper.models import CorperProfile

    CorperProfile.objects.create(
        user=user,
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )

    class MockRequest:
        auth = user

    resp = get_current_user(MockRequest())
    assert resp.email == "corper@example.com"
    assert resp.role == "corper"
    assert resp.corper_profile is not None
    assert resp.corper_profile.phone == "08012345678"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_current_user_vendor(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    from modules.vendor.models import VendorProfile

    VendorProfile.objects.create(
        user=user,
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )

    class MockRequest:
        auth = user

    resp = get_current_user(MockRequest())
    assert resp.email == "vendor@example.com"
    assert resp.role == "vendor"
    assert resp.vendor_profile is not None
    assert resp.vendor_profile.business_name == "Acme Ltd"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_forgot_password_success(USER, monkeypatch):
    USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    def mock_generate_token(user_id):
        return "reset_token_123"

    def mock_send_email(request, email, message):
        pass

    monkeypatch.setattr(
        "modules.authenticator.views.generate_password_reset_token", mock_generate_token
    )
    monkeypatch.setattr(
        "modules.authenticator.views.send_or_log_otp_email", mock_send_email
    )

    data = ForgotPasswordSchema(email="testuser@example.com")

    resp = forgot_password(object(), data)
    assert resp["success"] is True
    assert "token" in resp


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_forgot_password_user_not_found(USER):
    data = ForgotPasswordSchema(email="nonexistent@example.com")

    resp = forgot_password(object(), data)
    assert resp["success"] is True


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_password_success(USER, monkeypatch):
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    def mock_verify_token(token):
        return user.id, None

    monkeypatch.setattr(
        "modules.authenticator.views.verify_password_reset_token", mock_verify_token
    )

    data = ResetPasswordSchema(
        token="valid_token",
        new_password="newpass123!",
        confirm_password="newpass123!",
    )

    resp = reset_password(object(), data)
    assert resp["success"] is True

    user.refresh_from_db()
    assert user.check_password("newpass123!")


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_password_mismatch(USER):
    data = ResetPasswordSchema(
        token="valid_token",
        new_password="newpass123!",
        confirm_password="different123!",
    )

    with pytest.raises(HttpError) as exc_info:
        reset_password(object(), data)
    assert exc_info.value.status_code == 400


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_password_invalid_token(USER, monkeypatch):
    def mock_verify_token(token):
        return None, "Invalid token"

    monkeypatch.setattr(
        "modules.authenticator.views.verify_password_reset_token", mock_verify_token
    )

    data = ResetPasswordSchema(
        token="invalid_token",
        new_password="newpass123!",
        confirm_password="newpass123!",
    )

    with pytest.raises(HttpError) as exc_info:
        reset_password(object(), data)
    assert exc_info.value.status_code == 400
