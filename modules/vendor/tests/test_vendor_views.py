import pytest
from django.test import override_settings
from ninja.errors import HttpError

from modules.vendor.models import Vendor as VendorProfile
from modules.vendor.schemas import VendorProfileIn
from modules.vendor.views import get_vendor_profile, update_vendor_profile


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_vendor_profile_success(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    VendorProfile.objects.create(
        user=user,
        phone="08012345678",
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = get_vendor_profile(request)
    assert resp["email"] == "vendor@example.com"
    assert resp["business_name"] == "Acme Ltd"
    assert resp["phone"] == "08012345678"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_vendor_profile_not_found(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    with pytest.raises(HttpError) as exc_info:
        get_vendor_profile(request)
    assert exc_info.value.status_code == 404


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_vendor_profile_success(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    profile = VendorProfile.objects.create(
        user=user,
        phone="08012345678",
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = VendorProfileIn(
        years_in_operation=7,
    )

    resp = update_vendor_profile(request, data)
    assert resp.years_in_operation == 7

    profile.refresh_from_db()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_vendor_profile_not_found(USER):
    user = USER.objects.create_user(
        email="vendor@example.com",
        password="Password1!",
        is_active=True,
        role="vendor",
        full_name="Test Vendor",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = VendorProfileIn()

    with pytest.raises(HttpError) as exc_info:
        update_vendor_profile(request, data)
    assert exc_info.value.status_code == 404
