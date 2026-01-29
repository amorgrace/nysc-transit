import pytest
from pydantic_core._pydantic_core import ValidationError

from modules.vendor.schemas import VendorProfileIn, VendorProfileOut


def test_vendor_profile_out_valid():
    data = VendorProfileOut(
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )
    assert data.business_name == "Acme Ltd"
    assert data.years_in_operation == 5


def test_vendor_profile_out_minimal():
    data = VendorProfileOut(
        business_name="Acme Ltd",
        years_in_operation=5,
    )
    assert data.business_registration_number is None
    assert data.description is None


def test_vendor_profile_out_missing_required():
    with pytest.raises(ValidationError):
        VendorProfileOut(
            business_name="Acme Ltd",
            # missing years_in_operation
        )


def test_vendor_profile_in_all_fields():
    data = VendorProfileIn(
        business_name="Acme Ltd",
        business_registration_number="BRN12345",
        years_in_operation=5,
        description="We sell things",
    )
    assert data.business_name == "Acme Ltd"
    assert data.years_in_operation == 5


def test_vendor_profile_in_partial():
    data = VendorProfileIn(
        description="Updated description",
    )
    assert data.description == "Updated description"
    assert data.business_name is None
    assert data.years_in_operation is None


def test_vendor_profile_in_empty():
    data = VendorProfileIn()
    assert data.business_name is None
    assert data.business_registration_number is None
    assert data.years_in_operation is None
    assert data.description is None
