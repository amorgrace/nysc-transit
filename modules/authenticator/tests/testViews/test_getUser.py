from datetime import date
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model

from modules.authenticator.views import get_current_user
from modules.corper.models import CorperProfile
from modules.vendor.models import VendorProfile

VALID_PASSWORD = "Password@123"

User = get_user_model()


@pytest.mark.django_db
def test_get_current_user_corper_with_profile(USER):
    """Test getting current user data for corper with profile"""
    # Create corper user
    user = USER.objects.create_user(
        email="corper@example.com",
        password=VALID_PASSWORD,
        full_name="Test Corper",
        role="corper",
        phone="08012345678",
        is_active=True,
        email_verified=True,
    )

    # Create corper profile
    CorperProfile.objects.create(
        user=user,
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )

    # Mock request with authenticated user
    mock_request = Mock()
    mock_request.auth = user

    resp = get_current_user(mock_request)

    assert resp.id == user.id
    assert resp.email == "corper@example.com"
    assert resp.full_name == "Test Corper"
    assert resp.role == "corper"
    assert resp.phone == "08012345678"
    assert resp.is_active is True
    assert resp.email_verified is True
    assert resp.corper_profile is not None
    assert resp.corper_profile.phone == "08012345678"
    assert resp.corper_profile.state_code == "OS"
    assert resp.corper_profile.call_up_number == "12345"
    assert resp.corper_profile.deployment_state == "Lagos"
    assert resp.corper_profile.camp_location == "Camp A"
    assert resp.vendor_profile is None


@pytest.mark.django_db
def test_get_current_user_vendor_with_profile(USER):
    """Test getting current user data for vendor with profile"""
    # Create vendor user
    user = USER.objects.create_user(
        email="vendor@example.com",
        password=VALID_PASSWORD,
        full_name="Test Vendor",
        role="vendor",
        phone="07012345678",
        is_active=True,
        email_verified=True,
    )

    # Create vendor profile
    VendorProfile.objects.create(
        user=user,
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )

    # Mock request with authenticated user
    mock_request = Mock()
    mock_request.auth = user

    resp = get_current_user(mock_request)

    assert resp.id == user.id
    assert resp.email == "vendor@example.com"
    assert resp.full_name == "Test Vendor"
    assert resp.role == "vendor"
    assert resp.phone == "07012345678"
    assert resp.is_active is True
    assert resp.email_verified is True
    assert resp.vendor_profile is not None
    assert resp.vendor_profile.business_name == "Acme Ltd"
    assert resp.vendor_profile.business_registration_number == "BRN12345"
    assert resp.vendor_profile.years_in_operation == 5
    assert resp.vendor_profile.description == "We sell things"
    assert resp.corper_profile is None


@pytest.mark.django_db
def test_get_current_user_corper_without_profile(USER):
    """Test getting current user data for corper without profile"""
    # Create corper user without profile
    user = USER.objects.create_user(
        email="corper@example.com",
        password=VALID_PASSWORD,
        full_name="Test Corper",
        role="corper",
        phone="08012345678",
        is_active=True,
        email_verified=True,
    )

    # Mock request with authenticated user
    mock_request = Mock()
    mock_request.auth = user

    resp = get_current_user(mock_request)

    assert resp.id == user.id
    assert resp.email == "corper@example.com"
    assert resp.role == "corper"
    assert resp.corper_profile is None
    assert resp.vendor_profile is None


@pytest.mark.django_db
def test_get_current_user_vendor_without_profile(USER):
    """Test getting current user data for vendor without profile"""
    # Create vendor user without profile
    user = USER.objects.create_user(
        email="vendor@example.com",
        password=VALID_PASSWORD,
        full_name="Test Vendor",
        role="vendor",
        phone="07012345678",
        is_active=True,
        email_verified=True,
    )

    # Mock request with authenticated user
    mock_request = Mock()
    mock_request.auth = user

    resp = get_current_user(mock_request)

    assert resp.id == user.id
    assert resp.email == "vendor@example.com"
    assert resp.role == "vendor"
    assert resp.corper_profile is None
    assert resp.vendor_profile is None


@pytest.mark.django_db
def test_get_current_user_unauthenticated():
    """Test getting current user without authentication"""
    # Mock request without authenticated user
    mock_request = Mock()
    mock_request.auth = None

    with pytest.raises(Exception) as exc_info:
        get_current_user(mock_request)

    assert exc_info.value.status_code == 401
    assert "Authentication required" in str(exc_info.value)


@pytest.mark.django_db
def test_get_current_user_inactive_user(USER):
    """Test getting current user data for inactive user"""
    # Create inactive user
    user = USER.objects.create_user(
        email="inactive@example.com",
        password=VALID_PASSWORD,
        full_name="Inactive User",
        role="corper",
        is_active=False,
        email_verified=False,
    )

    # Mock request with authenticated user
    mock_request = Mock()
    mock_request.auth = user

    resp = get_current_user(mock_request)

    assert resp.id == user.id
    assert resp.email == "inactive@example.com"
    assert resp.is_active is False
    assert resp.email_verified is False


@pytest.mark.django_db
def test_get_current_user_all_fields_populated(USER):
    """Test that all user fields are correctly returned"""
    # Create user with all fields
    user = USER.objects.create_user(
        email="complete@example.com",
        password=VALID_PASSWORD,
        full_name="Complete User",
        role="corper",
        phone="08011111111",
        is_active=True,
        email_verified=True,
    )

    CorperProfile.objects.create(
        user=user,
        phone="08011111111",
        state_code="LA",
        call_up_number="99999",
        deployment_state="Ogun",
        camp_location="Camp B",
        deployment_date=date(2024, 1, 15),
    )

    # Mock request with authenticated user
    mock_request = Mock()
    mock_request.auth = user

    resp = get_current_user(mock_request)

    # Verify all fields
    assert resp.id == user.id
    assert resp.email == "complete@example.com"
    assert resp.full_name == "Complete User"
    assert resp.role == "corper"
    assert resp.phone == "08011111111"
    assert resp.is_active is True
    assert resp.email_verified is True
    assert resp.corper_profile is not None
    assert resp.corper_profile.deployment_date == date(2024, 1, 15)
    assert resp.vendor_profile is None
