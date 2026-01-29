from typing import List, Literal, Optional

from ninja import Schema


class VendorProfileOut(Schema):
    phone: Optional[str] = None
    business_name: Optional[str] = None
    business_registration_number: Optional[str] = None
    years_in_operation: int
    description: Optional[str] = None
    logo_url: Optional[str] = None
    verification_status: Optional[str] = None
    rejection_reason: Optional[str] = None
    rating_average: Optional[float] = None


class VendorProfileIn(Schema):
    phone: Optional[str] = None
    business_name: Optional[str] = None
    business_registration_number: Optional[str] = None
    years_in_operation: Optional[int] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    verification_documents: Optional[List[str]] = None
    payout_bank_name: Optional[str] = None
    payout_account_number: Optional[str] = None


class VendorUpdate(Schema):
    phone: Optional[str]
    business_name: Optional[str]
    business_registration_number: Optional[str]
    years_in_operation: Optional[int]
    verification_status: Optional[
        Literal["pending", "under_review", "verified", "rejected"]
    ]
    logo_url: Optional[str] = None
    verification_documents: Optional[List[str]] = None
    payout_bank_name: Optional[str] = None
    payout_account_number: Optional[str] = None
