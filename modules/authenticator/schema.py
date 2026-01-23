import re
from datetime import date

from ninja import Schema
from pydantic import BaseModel, EmailStr, field_validator


class CorperSignupSchema(Schema):
    # username: Optional[str] = None
    email: EmailStr
    password: str
    confirm_password: str
    full_name: str
    phone: str
    state_code: str
    call_up_number: str
    deployment_state: str
    camp_location: str
    deployment_date: date

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not v[0].isupper():
            raise ValueError("Password must start with a capital letter")
        if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]", v):
            raise ValueError("Password must contain at least one special character")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        v = v.strip()
        if not v.isdigit():
            raise ValueError("Phone must contain digits only")
        if len(v) != 11:
            raise ValueError("Phone number must be 11 digits")
        if not v.startswith("0"):
            raise ValueError("Phone number must start with 0")
        return v


class VendorSignupSchema(Schema):
    # username: Optional[str] = None
    email: EmailStr
    password: str
    confirm_password: str
    phone: str
    business_name: str
    business_registration_number: str
    years_in_operation: int
    description: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not v[0].isupper():
            raise ValueError("Password must start with a capital letter")
        if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]", v):
            raise ValueError("Password must contain at least one special character")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        v = v.strip()
        if not v.isdigit():
            raise ValueError("Phone must contain digits only")
        if len(v) != 11:
            raise ValueError("Phone number must be 11 digits")
        if not v.startswith("0"):
            raise ValueError("Phone number must start with 0")
        return v

    @field_validator("business_name", "business_registration_number")
    @classmethod
    def validate_business_fields(cls, v):
        if not v.strip():
            raise ValueError("Field cannot be empty")
        return v

    @field_validator("years_in_operation")
    @classmethod
    def validate_years(cls, v):
        if v < 0:
            raise ValueError("Years in operation cannot be negative")
        return v


class LoginSchema(Schema):
    email: EmailStr
    password: str


class LogoutSchema(Schema):
    refresh: str


class VerifyOTPSchema(BaseModel):
    email: EmailStr
    otp: str


class ResendOTPSchema(Schema):
    email: EmailStr
