from ninja import Schema
from datetime import date

class CorperSignupSchema(Schema):
    email: str
    password: str
    confirm_password: str
    full_name: str
    phone: str
    state_code: str
    call_up_number: str
    deployment_state: str
    camp_location: str
    deployment_date: date


class VendorSignupSchema(Schema):
    email: str
    password: str
    confirm_password: str
    phone: str
    business_name: str
    business_registration_number: str
    years_in_operation: int
    description: str

class LoginSchema(Schema):
    email: str
    password: str

class LogoutSchema(Schema):
    refresh: str