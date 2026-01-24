from datetime import date

import pytest
from pydantic_core._pydantic_core import ValidationError

from modules.corper.schemas import CorperProfileIn, CorperProfileOut


def test_corper_profile_out_valid():
    data = CorperProfileOut(
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )
    assert data.phone == "08012345678"
    assert data.state_code == "OS"
    assert data.call_up_number == "12345"


def test_corper_profile_out_missing_required_field():
    with pytest.raises(ValidationError):
        CorperProfileOut(
            phone="08012345678",
            state_code="OS",
            # missing call_up_number
            deployment_state="Lagos",
            camp_location="Camp A",
            deployment_date=date.today(),
        )


def test_corper_profile_in_all_fields():
    data = CorperProfileIn(
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )
    assert data.phone == "08012345678"
    assert data.state_code == "OS"


def test_corper_profile_in_partial_fields():
    data = CorperProfileIn(
        phone="08012345678",
        deployment_state="Lagos",
    )
    assert data.phone == "08012345678"
    assert data.deployment_state == "Lagos"
    assert data.state_code is None
    assert data.call_up_number is None


def test_corper_profile_in_empty():
    data = CorperProfileIn()
    assert data.phone is None
    assert data.state_code is None
    assert data.call_up_number is None
    assert data.deployment_state is None
