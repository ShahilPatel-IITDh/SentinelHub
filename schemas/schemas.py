from pydantic import BaseModel
from typing import List


class RegisterUser(BaseModel):
    name: str
    employee_id: str
    password: str
    designation: str
    reporting_officer_id: int


class LoginUser(BaseModel):
    employee_id: str
    password: str


class Heartbeat(BaseModel):
    mac_address: str
    hostname: str
    ip_address: str
    processes: List[str]