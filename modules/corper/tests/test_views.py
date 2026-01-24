from datetime import date

import pytest
from django.test import override_settings
from ninja.errors import HttpError

from modules.corper.schemas import CorperProfileIn
from modules.corper.views import get_corper_profile, update_corper_profile


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_corper_profile_success(USER):
    user = USER.objects.create_user(
        email="corper@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        full_name="Test Corper",
        phone="08011111111",
    )

    from modules.corper.models import CorperProfile

    CorperProfile.objects.create(
        user=user,
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    resp = get_corper_profile(request)
    assert resp["email"] == "corper@example.com"
    assert resp["full_name"] == "Test Corper"
    assert resp["role"] == "corper"
    assert resp["corper_phone"] == "08012345678"
    assert resp["state_code"] == "OS"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_get_corper_profile_not_found(USER):
    user = USER.objects.create_user(
        email="corper@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        full_name="Test Corper",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    with pytest.raises(HttpError) as exc_info:
        get_corper_profile(request)
    assert exc_info.value.status_code == 404


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_corper_profile_success(USER):
    user = USER.objects.create_user(
        email="corper@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        full_name="Test Corper",
    )

    from modules.corper.models import CorperProfile

    profile = CorperProfile.objects.create(
        user=user,
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = CorperProfileIn(
        phone="08099999999",
        deployment_state="Abuja",
        camp_location="Camp B",
    )

    resp = update_corper_profile(request, data)
    assert resp.phone == "08099999999"
    assert resp.deployment_state == "Abuja"
    assert resp.camp_location == "Camp B"

    profile.refresh_from_db()
    assert profile.phone == "08099999999"


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_corper_profile_not_found(USER):
    user = USER.objects.create_user(
        email="corper@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        full_name="Test Corper",
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = CorperProfileIn(phone="08099999999")

    with pytest.raises(HttpError) as exc_info:
        update_corper_profile(request, data)
    assert exc_info.value.status_code == 404


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_update_corper_profile_restricted_fields(USER):
    user = USER.objects.create_user(
        email="corper@example.com",
        password="Password1!",
        is_active=True,
        role="corper",
        full_name="Test Corper",
    )

    from modules.corper.models import CorperProfile

    CorperProfile.objects.create(
        user=user,
        phone="08012345678",
        state_code="OS",
        call_up_number="12345",
        deployment_state="Lagos",
        camp_location="Camp A",
        deployment_date=date.today(),
    )

    class MockRequest:
        pass

    request = MockRequest()
    request.user = user

    data = CorperProfileIn(state_code="LA")

    with pytest.raises(HttpError) as exc_info:
        update_corper_profile(request, data)
    assert exc_info.value.status_code == 400
