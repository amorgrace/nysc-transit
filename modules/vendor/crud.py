from .models import Vendor
from .schemas import VendorProfileIn, VendorUpdate


class VendorCRUD:
    def __init__(self, queryset=None):
        self.model = Vendor
        self.queryset = queryset or self.model.objects.all()

    def verify_vendor(self, vendor_id):
        """Mark a vendor as verified"""
        return self.queryset.filter(id=vendor_id).update(is_verified=True)

    def get_vendor_by_id(self, vendor_id):
        """Find a vendor by id"""
        return self.queryset.get(id=vendor_id)

    def get_all_vendors(self):
        """Get all vendors in the database"""
        return self.queryset.all()

    def create_vendor(self, data: VendorProfileIn, user=None):
        """create a vendor"""
        vendor_data = self.model.objects.create(
            user=user,
            phone=data.phone,
            business_name=data.business_name,
            business_registration_number=data.business_registration_number,
            years_in_operation=data.years_in_operation,
            logo_url=data.logo_url,
            verification_documents=data.verification_documents,
            payout_bank_name=data.payout_bank_name,
            payout_account_number=data.payout_account_number,
        )

        return vendor_data

    def update_fields(self, data: VendorUpdate, vendor_id):
        """Update vendor profile"""
        vendor = self.get_vendor_by_id(vendor_id=vendor_id)
        for field, value in data.dict(exclude_unset=True).items():
            setattr(vendor, field, value)
        vendor.save()
        return vendor

    def clear_fields(self, vendor_id, data: VendorUpdate):
        vendor = self.get_vendor_by_id(vendor_id=vendor_id)
        for field in data.dict(exclude_unset=True).keys():
            setattr(vendor, field, None)
        vendor.save()
        return vendor

    def delete_vendor(self, vendor_id):
        vendor = self.get_vendor_by_id(vendor_id=vendor_id)
        vendor.delete()
        return vendor
