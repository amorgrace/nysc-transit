import pytest
from django.test import override_settings

from modules.authenticator.utils.email import (
    generate_otp,
    send_or_log_otp_email,
    store_otp_for_user,
    verify_otp,
)


def test_generate_otp_length_and_digits():
    otp = generate_otp()
    assert isinstance(otp, str)
    assert len(otp) == 6
    assert otp.isdigit()


def test_send_or_log_otp_email_dev_mode_prints(capsys):
    with override_settings(DEBUG=True):
        send_or_log_otp_email(user=None, otp="123456", to_email="test@example.com")

    captured = capsys.readouterr()
    assert "DEV MODE - Would send email to: test@example.com" in captured.out
    assert (
        "Your verification code (OTP) is: 123456" in captured.out
        or "123456" in captured.out
    )


def test_send_or_log_otp_email_prod_calls_send_mail(monkeypatch):
    called = {}

    def fake_send_mail(
        subject,
        message,
        from_email,
        recipient_list,
        html_message=None,
        fail_silently=False,
    ):
        called["subject"] = subject
        called["message"] = message
        called["from_email"] = from_email
        called["recipient_list"] = recipient_list
        called["html_message"] = html_message
        called["fail_silently"] = fail_silently

    monkeypatch.setattr("modules.authenticator.utils.email.send_mail", fake_send_mail)

    with override_settings(DEBUG=False, DEFAULT_FROM_EMAIL="from@example.com"):
        send_or_log_otp_email(user=None, otp="654321", to_email="dest@example.com")

    assert called.get("recipient_list") == ["dest@example.com"]
    assert "654321" in (called.get("message") or "") or "654321" in (
        called.get("html_message") or ""
    )


@pytest.mark.django_db
def test_store_and_verify_otp_success(USER):
    user = USER.objects.create_user(
        email="u1@example.com", password="pass", role="corper"
    )
    store_otp_for_user(user, "000111", minutes=10)

    user.refresh_from_db()
    assert user.otp_code == "000111"

    ok, msg = verify_otp(user, "000111")
    assert ok is True
    assert "verified" in msg.lower()

    user.refresh_from_db()
    assert user.email_verified is True
    assert user.otp_code is None
    assert user.otp_expires_at is None


@pytest.mark.django_db
def test_verify_otp_invalid_code(USER):
    user = USER.objects.create_user(
        email="u2@example.com", password="pass", role="corper"
    )
    store_otp_for_user(user, "222333", minutes=10)

    ok, msg = verify_otp(user, "999999")
    assert ok is False
    assert msg == "Invalid OTP."

    user.refresh_from_db()
    assert user.email_verified is False
    assert user.otp_code == "222333"


@pytest.mark.django_db
def test_verify_otp_expired_clears_fields(USER):
    user = USER.objects.create_user(
        email="u3@example.com", password="pass", role="corper"
    )

    store_otp_for_user(user, "444555", minutes=-1)

    ok, msg = verify_otp(user, "444555")
    assert ok is False
    assert "expired" in msg.lower()

    user.refresh_from_db()
    assert user.otp_code is None
    assert user.otp_expires_at is None


@pytest.mark.django_db
def test_verify_otp_no_otp(USER):
    user = USER.objects.create_user(
        email="u4@example.com", password="pass", role="corper"
    )

    user.otp_code = None
    user.otp_expires_at = None
    user.save(update_fields=["otp_code", "otp_expires_at"])

    ok, msg = verify_otp(user, "000000")
    assert ok is False
    assert "no otp" in msg.lower()
