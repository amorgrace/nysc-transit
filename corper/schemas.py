from ninja import Schema
from datetime import date
from typing import Optional


class CorperProfileOut(Schema):
    phone: str
    state_code: str
    call_up_number: str
    deployment_state: str
    camp_location: str
    deployment_date: date


class CorperProfileIn(Schema):
    phone: Optional[str] = None
    state_code: Optional[str] = None
    call_up_number: Optional[str] = None
    deployment_state: Optional[str] = None
    camp_location: Optional[str] = None
    deployment_date: Optional[date] = None