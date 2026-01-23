import pytest
from django.contrib.auth.models import AnonymousUser
from ninja.errors import HttpError

from modules.authenticator.permissions import corper_required, vendor_required


class Request:
    def __init__(self, user):
        self.user = user


def test_corper_required_raises_401_when_no_user_attr():
    @corper_required
    def view(request):
        return "ok"

    request = object()  # no `user` attribute
    with pytest.raises(HttpError) as exc:
        view(request)

    assert exc.value.status_code == 401
    assert "Authentication required" in str(exc.value)


def test_corper_required_raises_401_when_user_not_authenticated():
    @corper_required
    def view(request):
        return "ok"

    request = Request(user=AnonymousUser())
    with pytest.raises(HttpError) as exc:
        view(request)

    assert exc.value.status_code == 401
    assert "Authentication required" in str(exc.value)


@pytest.mark.django_db
def test_corper_required_raises_403_for_wrong_role(USER):
    @corper_required
    def view(request):
        return "ok"

    user = USER.objects.create_user(
        email="vendor@example.com", password="pass", role="vendor"
    )
    request = Request(user=user)
    with pytest.raises(HttpError) as exc:
        view(request)

    assert exc.value.status_code == 403
    assert "Only corpers are allowed here" in str(exc.value)


@pytest.mark.django_db
def test_corper_required_allows_corper(USER):
    @corper_required
    def view(request):
        return "ok"

    user = USER.objects.create_user(
        email="corper@example.com", password="pass", role="corper"
    )
    request = Request(user=user)
    assert view(request) == "ok"


def test_vendor_required_raises_401_when_not_authenticated():
    @vendor_required
    def view(request):
        return "ok"

    request = Request(user=AnonymousUser())
    with pytest.raises(HttpError) as exc:
        view(request)

    assert exc.value.status_code == 401
    assert "Authentication required" in str(exc.value)


@pytest.mark.django_db
def test_vendor_required_raises_403_for_wrong_role(USER):
    @vendor_required
    def view(request):
        return "ok"

    user = USER.objects.create_user(
        email="corper2@example.com", password="pass", role="corper"
    )
    request = Request(user=user)
    with pytest.raises(HttpError) as exc:
        view(request)

    assert exc.value.status_code == 403
    assert "Only vendors are allowed here" in str(exc.value)


@pytest.mark.django_db
def test_vendor_required_allows_vendor(USER):
    @vendor_required
    def view(request):
        return "ok"

    user = USER.objects.create_user(
        email="vendor2@example.com", password="pass", role="vendor"
    )
    request = Request(user=user)
    assert view(request) == "ok"
