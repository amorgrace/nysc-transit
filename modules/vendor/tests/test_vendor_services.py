import pytest

from modules.vendor.schemas import VendorProfileIn
from modules.vendor.services import VendorService


@pytest.mark.django_db
def test_vendor_service_profile_and_delete(USER):
    user = USER.objects.create_user(
        email="vendorsvc@example.com", password="pass", role="vendor"
    )

    svc = VendorService()

    # create profile via CRUD through service.create_vendor
    payload = VendorProfileIn(
        phone="08099998877",
        business_name="ServiceCo",
        business_registration_number="BRNSVC01",
        years_in_operation=2,
        payout_bank_name="Bank",
        payout_account_number="000111",
    )

    profile = svc.create_vendor(payload, user=user)
    assert profile.user == user

    # get profile data
    data = svc.get_profile_data(user)
    assert data["email"] == user.email
    assert data["business_name"] == "ServiceCo"

    # update profile
    upd = VendorProfileIn(years_in_operation=10)
    updated = svc.update_profile(user, upd)
    assert updated.years_in_operation == 10

    # delete via service (soft)
    deleted = svc.delete_vendor(profile.pk)
    assert deleted.is_active is False
