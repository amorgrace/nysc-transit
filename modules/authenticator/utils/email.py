import random
import string
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


def generate_otp(length=6):
    """Generate a random numeric OTP"""
    return "".join(random.choices(string.digits, k=length))


def send_or_log_otp_email(user, otp: str, to_email: str):
    """
    In dev: logs to console + returns content
    In prod: actually sends via SMTP
    """
    subject = "Your NYSC Corper Verification Code"
    message = (
        f"Welcome to NYSC service!\n\n"
        f"Your verification code (OTP) is: {otp}\n\n"
        f"This code expires in 10 minutes.\n"
        f"Do not share this code with anyone.\n\n"
        f"Thanks,\nNYSC App Team"
    )

    html_message = f"""
    <html>
    <body>
        <h2>Welcome to NYSC Service!</h2>
        <p>Your verification code is:</p>
        <h1 style="font-size: 32px; letter-spacing: 8px;">{otp}</h1>
        <p>This code expires in 10 minutes.</p>
        <p>Do not share this code with anyone.</p>
        <br>
        <p>Thanks,<br>NYSC App Team</p>
    </body>
    </html>
    """

    if settings.DEBUG:
        # Print full email to console (visible in terminal)
        print("\n" + "=" * 80)
        print(f"DEV MODE - Would send email to: {to_email}")
        print(f"Subject: {subject}")
        print("Body (plain):\n" + message)
        print("Body (HTML):\n" + html_message)
        print("=" * 80 + "\n")
        return  # don't actually send

    # Real send (when DEBUG=False and SMTP configured)
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to_email],
        html_message=html_message,
        fail_silently=False,
    )


def store_otp_for_user(user, otp: str, minutes=10):
    """Save OTP + expiry to user model"""
    user.otp_code = otp
    user.otp_expires_at = timezone.now() + timedelta(minutes=minutes)
    user.save(update_fields=["otp_code", "otp_expires_at"])


def verify_otp(user, entered_otp: str) -> tuple[bool, str]:
    """Check if OTP is valid and not expired"""
    if not user.otp_code or not user.otp_expires_at:
        return False, "No OTP found. Request a new one."

    if timezone.now() > user.otp_expires_at:
        user.otp_code = None
        user.otp_expires_at = None
        user.save(update_fields=["otp_code", "otp_expires_at"])
        return False, "OTP has expired. Request a new one."

    if user.otp_code != entered_otp:
        return False, "Invalid OTP."

    # Success → clean up
    user.otp_code = None
    user.otp_expires_at = None
    user.email_verified = True
    user.save(update_fields=["otp_code", "otp_expires_at", "email_verified"])

    return True, "Email verified successfully!"
