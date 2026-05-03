from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from db.database import SessionLocal
from db.models import User, SystemMetrics, ErrorLog
from schemas.schemas import Heartbeat
from services.heartbeat_service import process_heartbeat
from services.log_service import get_manager_logs
from services.summary_service import get_summary

from core.security import decode_token
from core.logger import logger

router = APIRouter(prefix="/api/node")
security = HTTPBearer()


# ---------------- DB ---------------- #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- AUTH ---------------- #

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        user_id = decode_token(token)

        user = db.query(User).filter(
            User.employee_id == user_id
        ).first()

        if not user:
            raise HTTPException(401, "User not found")

        return user

    except Exception as e:
        logger.warning(f"[AUTH] Invalid token: {str(e)}")
        raise HTTPException(401, "Invalid or expired token")


# ---------------- HELPER ---------------- #

def validate_manager_access(user: User, manager_id: int):
    if not user.designation or user.designation.lower() != "manager":
        logger.warning(f"[SECURITY] Non-manager access attempt: {user.employee_id}")
        raise HTTPException(403, "Only managers allowed")

    if user.employee_id != manager_id:
        logger.warning(f"[SECURITY] Unauthorized access: {user.employee_id} -> {manager_id}")
        raise HTTPException(403, "Access denied")


def get_team_employee_ids(db: Session, manager_id: int):
    employees = db.query(User.employee_id).filter(
        User.reporting_officer_id == manager_id
    ).all()

    ids = [e.employee_id for e in employees]
    ids.append(manager_id)
    return ids


# ---------------- HEARTBEAT ---------------- #

@router.post("/heartbeat")
def heartbeat(
    data: Heartbeat,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    logger.info(f"[ROUTE] Heartbeat from {user.employee_id}")
    return process_heartbeat(db, data, user.employee_id)


# ---------------- LOGS ---------------- #

@router.get("/logs/{manager_id}")
def get_logs(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    validate_manager_access(user, manager_id)

    logger.info(f"[ROUTE] Logs requested by {user.employee_id}")

    return get_manager_logs(db, manager_id)


# ---------------- SUMMARY ---------------- #

@router.get("/summary/{manager_id}")
def summary(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    validate_manager_access(user, manager_id)

    logger.info(f"[ROUTE] Summary requested by {user.employee_id}")

    return get_summary(db, manager_id)


# ---------------- METRICS ---------------- #

@router.get("/metrics/{manager_id}")
def get_metrics(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    validate_manager_access(user, manager_id)

    logger.info(f"[ROUTE] Metrics requested by {user.employee_id}")

    employee_ids = get_team_employee_ids(db, manager_id)

    metrics = (
        db.query(SystemMetrics)
        .filter(SystemMetrics.employee_id.in_(employee_ids))
        .order_by(SystemMetrics.timestamp.desc())
        .limit(500)
        .all()
    )

    return [
        {
            "mac_address": m.mac_address,
            "employee_id": m.employee_id,
            "cpu": m.cpu_percent,
            "memory": m.memory_percent,
            "disk": m.disk_percent,
            "timestamp": m.timestamp
        }
        for m in metrics
    ]


# ---------------- ERROR LOGS ---------------- #

@router.get("/errors/{manager_id}")
def get_errors(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    validate_manager_access(user, manager_id)

    logger.info(f"[ROUTE] Errors requested by {user.employee_id}")

    employee_ids = get_team_employee_ids(db, manager_id)

    errors = (
        db.query(ErrorLog)
        .filter(ErrorLog.employee_id.in_(employee_ids))
        .order_by(ErrorLog.timestamp.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "mac_address": e.mac_address,
            "employee_id": e.employee_id,
            "error_type": e.error_type,
            "message": e.message,
            "severity": e.severity,
            "timestamp": e.timestamp
        }
        for e in errors
    ]