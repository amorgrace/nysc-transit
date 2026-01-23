from datetime import date

import pytest
from pydantic import ValidationError

from modules.authenticator.schema import CorperSignupSchema, VendorSignupSchema


@pytest.mark.parametrize(
    "phone",
    [
        "08012345678",
        " 08012345678 ",
    ],
)
@pytest.mark.parametrize("password", ["Abcdef!1", "Xyz123$1"])
def test_valid_corper_fields(phone, password):
    """Test that all input fields are validated correctly"""
    user = CorperSignupSchema(
        email="test@example.com",
        password=password,
        confirm_password=password,
        full_name="John Doe",
        phone=phone,
        state_code="AB",
        call_up_number="12345",
        deployment_state="State",
        camp_location="Camp",
        deployment_date=date(2026, 1, 22),
    )

    assert user.phone == "08012345678"

    assert user.password == password
    assert user.confirm_password == password


@pytest.mark.parametrize(
    "phone",
    [
        "0801234567",
        "080123456789",
        "08012A45678",
        "+2348012345678",
        "8012345678",
    ],
)
def test_invalid_corper_phone(phone):
    """Test Edge Cases that shouldn't be accepted in phone field"""
    password = "Abcdef!1"
    with pytest.raises(ValidationError):
        CorperSignupSchema(
            email="test@example.com",
            password=password,
            confirm_password=password,
            full_name="John Doe",
            phone=phone,
            state_code="AB",
            call_up_number="12345",
            deployment_state="State",
            camp_location="Camp",
            deployment_date=date(2026, 1, 22),
        )


@pytest.mark.parametrize(
    "password",
    [
        "abcdef!1",
        "Abcdefgh1",
        "Ab1!",
    ],
)
def test_invalid_corper_password(password):
    phone = "08012345678"
    with pytest.raises(ValidationError):
        CorperSignupSchema(
            email="test@example.com",
            password=password,
            confirm_password=password,
            full_name="John Doe",
            phone=phone,
            state_code="AB",
            call_up_number="12345",
            deployment_state="State",
            camp_location="Camp",
            deployment_date=date(2026, 1, 22),
        )


def test_corper_password_mismatch():
    phone = "08012345678"
    password = "Abcdef!1"
    confirm_password = "Xyz123$1"
    with pytest.raises(ValidationError):
        CorperSignupSchema(
            email="test@example.com",
            password=password,
            confirm_password=confirm_password,
            full_name="John Doe",
            phone=phone,
            state_code="AB",
            call_up_number="12345",
            deployment_state="State",
            camp_location="Camp",
            deployment_date=date(2026, 1, 22),
        )


@pytest.mark.parametrize("phone", ["08012345678", " 08012345678 "])
@pytest.mark.parametrize("password", ["Abcdef!1", "Xyz123$1"])
def test_valid_vendor_fields(phone, password):
    vendor = VendorSignupSchema(
        email="vendor@example.com",
        password=password,
        confirm_password=password,
        phone=phone,
        business_name="Test Biz",
        business_registration_number="BRN123",
        years_in_operation=5,
        description="A vendor",
    )

    assert vendor.phone == "08012345678"
    assert vendor.business_name == "Test Biz"
    assert vendor.business_registration_number == "BRN123"
    assert vendor.years_in_operation == 5
    assert vendor.description == "A vendor"


@pytest.mark.parametrize(
    "phone",
    ["0801234567", "080123456789", "08012A45678", "+2348012345678", "8012345678"],
)
def test_invalid_vendor_phone(phone):
    password = "Abcdef!1"
    with pytest.raises(ValidationError):
        VendorSignupSchema(
            email="vendor@example.com",
            password=password,
            confirm_password=password,
            phone=phone,
            business_name="Test Biz",
            business_registration_number="BRN123",
            years_in_operation=5,
            description="A vendor",
        )


@pytest.mark.parametrize("password", ["abcdef!1", "Abcdefgh1", "Ab1!"])
def test_invalid_vendor_password(password):
    phone = "08012345678"
    with pytest.raises(ValidationError):
        VendorSignupSchema(
            email="vendor@example.com",
            password=password,
            confirm_password=password,
            phone=phone,
            business_name="Test Biz",
            business_registration_number="BRN123",
            years_in_operation=5,
            description="A vendor",
        )


def test_vendor_password_mismatch():
    phone = "08012345678"
    password = "Abcdef!1"
    confirm_password = "Xyz123$1"
    with pytest.raises(ValidationError):
        VendorSignupSchema(
            email="vendor@example.com",
            password=password,
            confirm_password=confirm_password,
            phone=phone,
            business_name="Test Biz",
            business_registration_number="BRN123",
            years_in_operation=5,
            description="A vendor",
        )
