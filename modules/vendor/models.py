from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Vendor(models.Model):
    VERIFICATION_PENDING = "pending"
    VERIFICATION_UNDER_REVIEW = "under_review"
    VERIFICATION_APPROVED = "verified"
    VERIFICATION_REJECTED = "rejected"

    VERIFICATION_CHOICES = [
        (VERIFICATION_PENDING, "Pending"),
        (VERIFICATION_UNDER_REVIEW, "Under Review"),
        (VERIFICATION_APPROVED, "Verified"),
        (VERIFICATION_REJECTED, "Rejected"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vendor_profile",
    )
    phone = models.CharField(max_length=15)
    business_name = models.CharField(max_length=150)
    business_registration_number = models.CharField(max_length=100, unique=True)
    years_in_operation = models.PositiveIntegerField()
    logo_url = models.URLField(blank=True, null=True)
    verification_documents = models.JSONField(blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default=VERIFICATION_PENDING,
    )
    rejection_reason = models.TextField(blank=True, null=True)
    rating_average = models.FloatField(
        default=0.0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    payout_bank_name = models.CharField(max_length=100, blank=True)
    payout_account_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendors"

    @property
    def is_verified(self):
        return self.verification_status == self.VERIFICATION_APPROVED
