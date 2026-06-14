from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from schemas.schemas import (
    RegisterUser,
    LoginUser,
    AssignManager,
    UpdateDesignation,
    CreatePost,
    UpdateUserPost,
    AssignReportingOfficer
)
from services.auth_service import (
    register_user,
    login_user,
    assign_manager,
    update_designation,
    create_post,
    update_user_post,
    assign_reporting_officer
)
from core.dependencies import get_db, require_hierarchy_admin
from db.models import User
import re

router = APIRouter(prefix="/api/auth")


# # ---------------- DB ---------------- #
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# ---------------- PASSWORD VALIDATION ---------------- #
BCRYPT_MAX_PASSWORD_BYTES = 72


def validate_password_byte_length(password: str):
    if len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
        raise HTTPException(
            400,
            "Password cannot exceed 72 bytes (bcrypt limit)",
        )


def validate_password(password: str):
    validate_password_byte_length(password)

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
    validate_password_byte_length(data.password)
    return login_user(db, data)

#--------Adding New Routes for Hierarchy Management--------#

@router.post("/posts")
def create_post_route(
    data: CreatePost,
    db: Session = Depends(get_db),
    admin: User = Depends(require_hierarchy_admin)
):
    return create_post(db, data)


@router.put("/update-post")
def update_post_route(
    data: UpdateUserPost,
    db: Session = Depends(get_db),
    admin: User = Depends(require_hierarchy_admin)
):
    return update_user_post(db, data.employee_id, data.post_id)


@router.put("/assign-reporting-officer")
def assign_reporting_officer_route(
    data: AssignReportingOfficer,
    db: Session = Depends(get_db),
    admin: User = Depends(require_hierarchy_admin)
):
    return assign_reporting_officer(
        db,
        data.employee_id,
        data.reporting_officer_id
    )

# ---------------- MANAGEMENT ---------------- #

@router.put("/assign-manager")
def assign_manager_route(data: AssignManager, db: Session = Depends(get_db), admin: User = Depends(require_hierarchy_admin)):
    return assign_manager(db, data.employee_id, data.manager_id)


@router.put("/update-designation")
def update_designation_route(data: UpdateDesignation, db: Session = Depends(get_db), admin: User = Depends(require_hierarchy_admin)):
    return update_designation(db, data.employee_id, data.designation)