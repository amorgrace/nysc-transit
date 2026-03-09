from django.apps import AppConfig


class BookingsConfig(AppConfig):
    name = "modules.bookings"

    def ready(self):
        from . import signals

        _ = signals
