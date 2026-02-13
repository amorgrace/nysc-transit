from typing import Any, cast

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def apply_migrations(django_db_blocker):
    """Ensure migrations are applied once for the entire test session."""
    with django_db_blocker.unblock():
        try:
            call_command("makemigrations", "--noinput")
        except SystemExit:
            pass
        call_command("migrate", "--noinput")

        call_command("flush", "--noinput", allow_cascade=True)


@pytest.fixture(scope="session")
def USER() -> Any:
    """Return the project user model cast to Any to avoid static type complaints.

    Tests can accept the `USER` fixture and call `USER.objects.create_user(...)`.
    """
    return cast(Any, get_user_model())
