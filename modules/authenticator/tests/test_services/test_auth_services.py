import pytest
from django.test import override_settings
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from modules.authenticator.schema import (
    ForgotPasswordSchema,
    LoginSchema,
    LogoutSchema,
    ResendOTPSchema,
    ResetPasswordSchema,
    VerifyOTPSchema,
)
from modules.authenticator.services.auth_service import (
    forgot_password_service,
    login_service,
    logout_service,
    resend_otp_service,
    reset_password_service,
    verify_otp_service,
)

# ============================================================================
# LOGIN SERVICE TESTS
# ============================================================================


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


# ============================================================================
# LOGOUT SERVICE TESTS
# ============================================================================


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


# ============================================================================
# VERIFY OTP SERVICE TESTS
# ============================================================================


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


# ============================================================================
# RESEND OTP SERVICE TESTS
# ============================================================================


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_resend_otp_service_success_debug_mode(USER, monkeypatch):
    """Test resend OTP success in DEBUG mode - OTP should be exposed"""
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
        "modules.authenticator.services.auth_service.generate_otp",
        lambda: "123456",
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.store_otp_for_user",
        lambda u, otp: None,
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.send_or_log_otp_email",
        lambda u, otp, email: None,
    )

    data = ResendOTPSchema(email="testuser@example.com")
    resp = resend_otp_service(data)

    assert resp["success"] is True
    assert resp["message"] == "OTP resent successfully"
    assert "otp" in resp  # OTP should be exposed in DEBUG mode
    assert resp["otp"] == "123456"


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_resend_otp_service_success_production_mode(USER, monkeypatch):
    """Test resend OTP success in production mode - OTP should NOT be exposed"""
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
        "modules.authenticator.services.auth_service.generate_otp",
        lambda: "123456",
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.store_otp_for_user",
        lambda u, otp: None,
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.send_or_log_otp_email",
        lambda u, otp, email: None,
    )

    data = ResendOTPSchema(email="testuser@example.com")
    resp = resend_otp_service(data)

    assert resp["success"] is True
    assert resp["message"] == "OTP resent successfully"
    assert "otp" not in resp  # OTP should NOT be exposed in production


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_resend_otp_service_user_not_found(USER, monkeypatch):
    """Test resend OTP when user doesn't exist"""
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: None,
    )

    data = ResendOTPSchema(email="nonexistent@example.com")
    with pytest.raises(HttpError) as exc_info:
        resend_otp_service(data)

    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_resend_otp_service_user_already_verified(USER, monkeypatch):
    """Test resend OTP when user is already verified/active"""
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,  # Already active/verified
    )

    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: user,
    )

    data = ResendOTPSchema(email="testuser@example.com")
    with pytest.raises(HttpError) as exc_info:
        resend_otp_service(data)

    assert exc_info.value.status_code == 400
    assert "User already verified" in str(exc_info.value)


# ============================================================================
# FORGOT PASSWORD SERVICE TESTS
# ============================================================================


@pytest.mark.django_db
@override_settings(DEBUG=True, FRONTEND_URL="http://localhost:3000")
def test_forgot_password_service_success_debug_mode(USER, monkeypatch):
    """Test forgot password success in DEBUG mode - token should be exposed"""
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: user,
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.generate_password_reset_token",
        lambda user_id: "reset_token_12345",
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.send_or_log_otp_email",
        lambda user, email, message: None,
    )

    data = ForgotPasswordSchema(email="testuser@example.com")
    resp = forgot_password_service(data)

    assert resp["success"] is True
    assert resp["message"] == "If your email exists, a reset link has been sent"
    assert "token" in resp  # Token should be exposed in DEBUG mode
    assert resp["token"] == "reset_token_12345"


@pytest.mark.django_db
@override_settings(DEBUG=False, FRONTEND_URL="http://localhost:3000")
def test_forgot_password_service_success_production_mode(USER, monkeypatch):
    """Test forgot password success in production mode - token should NOT be exposed"""
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="Password1!",
        is_active=True,
    )

    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: user,
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.generate_password_reset_token",
        lambda user_id: "reset_token_12345",
    )
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.send_or_log_otp_email",
        lambda user, email, message: None,
    )

    data = ForgotPasswordSchema(email="testuser@example.com")
    resp = forgot_password_service(data)

    assert resp["success"] is True
    assert resp["message"] == "If your email exists, a reset link has been sent"
    assert "token" not in resp  # Token should NOT be exposed in production


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_forgot_password_service_user_not_found(USER, monkeypatch):
    """
    Test forgot password when user doesn't exist.
    Should still return success to prevent email enumeration.
    """
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.get_user_by_email",
        lambda email: None,
    )

    data = ForgotPasswordSchema(email="nonexistent@example.com")
    resp = forgot_password_service(data)

    # Should still return success for security (prevent email enumeration)
    assert resp["success"] is True
    assert resp["message"] == "If your email exists, a reset link has been sent"
    assert "token" not in resp  # No token when user doesn't exist


# ============================================================================
# RESET PASSWORD SERVICE TESTS
# ============================================================================


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_password_service_success(USER, monkeypatch):
    """Test successful password reset"""
    user = USER.objects.create_user(
        email="testuser@example.com",
        password="OldPassword1!",
        is_active=True,
    )

    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.verify_password_reset_token",
        lambda token: (user.id, None),  # Returns (user_id, None) on success
    )

    password_updated = False

    def mock_update_password(u, new_password):
        nonlocal password_updated
        password_updated = True
        u.set_password(new_password)
        u.save()

    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.update_user_password",
        mock_update_password,
    )

    data = ResetPasswordSchema(
        token="valid_reset_token",
        new_password="NewPassword1!",
        confirm_password="NewPassword1!",
    )
    resp = reset_password_service(data)

    assert resp["success"] is True
    assert resp["message"] == "Password reset successfully"
    assert password_updated is True


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_password_service_password_mismatch(USER, monkeypatch):
    """Test reset password when passwords don't match"""
    data = ResetPasswordSchema(
        token="valid_reset_token",
        new_password="NewPassword1!",
        confirm_password="DifferentPassword1!",
    )

    with pytest.raises(HttpError) as exc_info:
        reset_password_service(data)

    assert exc_info.value.status_code == 400
    assert "Passwords do not match" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_password_service_invalid_token(USER, monkeypatch):
    """Test reset password with invalid/expired token"""
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.verify_password_reset_token",
        lambda token: (None, "Invalid or expired reset token"),
    )

    data = ResetPasswordSchema(
        token="invalid_token",
        new_password="NewPassword1!",
        confirm_password="NewPassword1!",
    )

    with pytest.raises(HttpError) as exc_info:
        reset_password_service(data)

    assert exc_info.value.status_code == 400
    assert "Invalid or expired reset token" in str(exc_info.value)


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_reset_password_service_user_not_found(USER, monkeypatch):
    """Test reset password when user ID from token doesn't exist"""
    # Token is valid but user with that ID doesn't exist
    monkeypatch.setattr(
        "modules.authenticator.services.auth_service.verify_password_reset_token",
        lambda token: (99999, None),  # Non-existent user ID
    )

    data = ResetPasswordSchema(
        token="valid_token_for_deleted_user",
        new_password="NewPassword1!",
        confirm_password="NewPassword1!",
    )

    with pytest.raises(HttpError) as exc_info:
        reset_password_service(data)

    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value)
