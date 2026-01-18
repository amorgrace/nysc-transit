import uuid

from django.conf import settings
from django.db import models


class CorperProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="corper_profile",
    )
    phone = models.CharField(max_length=15)
    state_code = models.CharField(max_length=20)
    call_up_number = models.CharField(max_length=30, unique=True)
    deployment_state = models.CharField(max_length=100)
    camp_location = models.CharField(max_length=150)
    deployment_date = models.DateField()
