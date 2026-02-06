import pytest

from modules.vendor.crud import VendorCRUD
from modules.vendor.schemas import VendorProfileIn


@pytest.mark.django_db
def test_vendor_crud_create_update_clear_delete(USER):
    user = USER.objects.create_user(
        email="vendorcrud@example.com", password="pass", role="vendor"
    )

    crud = VendorCRUD()

    payload = VendorProfileIn(
        phone="08012345678",
        business_name="Acme Ltd",
        business_registration_number="BRN0001",
        years_in_operation=3,
        payout_bank_name="First Bank",
        payout_account_number="000111222",
    )

    profile = crud.create_vendor(data=payload, user=user)
    assert profile.user == user
    assert profile.business_name == "Acme Ltd"

    # get by id
    got = crud.get_vendor_by_id(getattr(profile, "id"))
    assert getattr(got, "id") == getattr(profile, "id")

    # update fields
    upd = VendorProfileIn(years_in_operation=5)
    updated = crud.update_fields(data=upd, vendor_id=getattr(profile, "id"))
    assert updated.years_in_operation == 5

    # clear a nullable field (logo_url)
    cleared = crud.clear_fields(
        vendor_id=getattr(profile, "id"), data=VendorProfileIn(logo_url="x")
    )
    assert cleared.logo_url is None

    # delete (soft)
    deleted = crud.delete_vendor(vendor_id=getattr(profile, "id"))
    assert deleted.is_active is False

    # get_all_vendors should not include the soft-deleted profile
    all_vendors = crud.get_all_vendors()
    assert profile not in list(all_vendors)
