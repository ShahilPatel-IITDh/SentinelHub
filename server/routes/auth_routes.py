from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from schemas.schemas import (
    RegisterUser,
    LoginUser,
    AssignManager,
    UpdateDesignation
)
from services.auth_service import (
    register_user,
    login_user,
    assign_manager,
    update_designation
)
import re

router = APIRouter(prefix="/api/auth")


# ---------------- DB ---------------- #
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- PASSWORD VALIDATION ---------------- #
def validate_password(password: str):
    if len(password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")

    if not re.search(r"[A-Z]", password):
        raise HTTPException(400, "Password must contain an uppercase letter")

    if not re.search(r"[a-z]", password):
        raise HTTPException(400, "Password must contain a lowercase letter")

    if not re.search(r"[0-9]", password):
        raise HTTPException(400, "Password must contain a number")

    if not re.search(r"[!@#$%^&*]", password):
        raise HTTPException(400, "Password must contain a special character")


# ---------------- ROUTES ---------------- #

@router.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    validate_password(user.password)
    return register_user(db, user)


@router.post("/login")
def login(data: LoginUser, db: Session = Depends(get_db)):
    return login_user(db, data)


# ---------------- MANAGEMENT ---------------- #

@router.put("/assign-manager")
def assign_manager_route(data: AssignManager, db: Session = Depends(get_db)):
    return assign_manager(db, data.employee_id, data.manager_id)


@router.put("/update-designation")
def update_designation_route(data: UpdateDesignation, db: Session = Depends(get_db)):
    return update_designation(db, data.employee_id, data.designation)