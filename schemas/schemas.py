from pydantic import BaseModel
from typing import List, Optional


# ---------------- AUTH ---------------- #

class RegisterUser(BaseModel):
    name: str
    employee_id: int
    password: str
    designation: str
    reporting_officer_id: Optional[int] = None   # ✅ FIXED


class LoginUser(BaseModel):
    employee_id: int
    password: str


# ---------------- HEARTBEAT ---------------- #

class Heartbeat(BaseModel):
    mac_address: str
    hostname: str
    ip_address: str
    processes: List[str]