from django.db import models
from django.conf import settings

class VendorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=150)
    business_registration_number = models.CharField(max_length=100, unique=True)
    years_in_operation = models.PositiveIntegerField()
    description = models.TextField()
