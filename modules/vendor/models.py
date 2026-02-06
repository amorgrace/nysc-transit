from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ninja.errors import ValidationError


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
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "vendors"

    def _update_verification_status(self):
        if self.verification_status in {
            self.VERIFICATION_APPROVED,
            self.VERIFICATION_REJECTED,
        }:
            return

        if self.business_name and self.business_registration_number:
            self.verification_status = self.VERIFICATION_UNDER_REVIEW
        else:
            self.verification_status = self.VERIFICATION_PENDING

    def clean(self):
        if (
            self.verification_status == self.VERIFICATION_REJECTED
            and not self.rejection_reason
        ):
            raise ValidationError(
                [{"rejection_reason": "Rejection reason is required."}]
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        self._update_verification_status()
        super().save(*args, **kwargs)
