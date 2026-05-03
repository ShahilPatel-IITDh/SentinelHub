from pydantic import BaseModel, Field
from typing import List, Optional


# ---------------- AUTH ---------------- #

class RegisterUser(BaseModel):
    name: str
    employee_id: int
    password: str
    designation: str
    reporting_officer_id: Optional[int] = None


class LoginUser(BaseModel):
    employee_id: int
    password: str


# ---------------- MANAGEMENT ---------------- #

class AssignManager(BaseModel):
    employee_id: int
    manager_id: int


class UpdateDesignation(BaseModel):
    employee_id: int
    designation: str


# ---------------- HEARTBEAT ---------------- #

class Heartbeat(BaseModel):
    mac_address: str
    hostname: str
    ip_address: str
    processes: List[str]

    cpu_percent: float = Field(..., ge=0, le=100)
    memory_percent: float = Field(..., ge=0, le=100)
    disk_percent: float = Field(..., ge=0, le=100)


# ---------------- ERROR ---------------- #

class ErrorLogSchema(BaseModel):
    mac_address: str
    error_message: str
    severity: str