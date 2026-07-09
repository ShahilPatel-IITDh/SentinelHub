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

from core.dependencies import get_db, get_current_user
from services.hierarchy_service import get_direct_monitorable_junior_ids
from services.log_service import get_logs_for_employee_ids
from services.summary_service import get_summary_for_employee_ids
from services.metrics_service import get_metrics_for_employee_ids
from services.error_service import get_errors_for_employee_ids
from services.dashboard_service import get_dashboard_live_data

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
def get_logs_old(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # Backward compatibility check
    # Old dashboard sends manager_id in URL.
    # But logged-in user must match that ID.
    if user.employee_id != manager_id:
        logger.warning(
            f"[SECURITY] Unauthorized old logs route access: "
            f"{user.employee_id} tried to access {manager_id}"
        )
        raise HTTPException(status_code=403, detail="Access denied")

    junior_ids = get_direct_monitorable_junior_ids(db, user)

    logger.info(
        f"[ROUTE] Old logs route used by {user.employee_id}; "
        f"direct juniors: {junior_ids}"
    )

    return get_logs_for_employee_ids(db, junior_ids)


# ---------------- SUMMARY ---------------- #

@router.get("/summary/{manager_id}")
def summary_old(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.employee_id != manager_id:
        logger.warning(
            f"[SECURITY] Unauthorized old summary route access: "
            f"{user.employee_id} tried to access {manager_id}"
        )
        raise HTTPException(status_code=403, detail="Access denied")

    junior_ids = get_direct_monitorable_junior_ids(db, user)

    logger.info(
        f"[ROUTE] Old summary route used by {user.employee_id}; "
        f"direct juniors: {junior_ids}"
    )

    return get_summary_for_employee_ids(db, junior_ids)


# ---------------- METRICS ---------------- #

@router.get("/metrics/{manager_id}")
def get_metrics_old(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.employee_id != manager_id:
        logger.warning(
            f"[SECURITY] Unauthorized old metrics route access: "
            f"{user.employee_id} tried to access {manager_id}"
        )
        raise HTTPException(status_code=403, detail="Access denied")

    junior_ids = get_direct_monitorable_junior_ids(db, user)

    if not junior_ids:
        return []

    metrics = (
        db.query(SystemMetrics)
        .filter(SystemMetrics.employee_id.in_(junior_ids))
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
def get_errors_old(
    manager_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.employee_id != manager_id:
        logger.warning(
            f"[SECURITY] Unauthorized old errors route access: "
            f"{user.employee_id} tried to access {manager_id}"
        )
        raise HTTPException(status_code=403, detail="Access denied")

    junior_ids = get_direct_monitorable_junior_ids(db, user)

    if not junior_ids:
        return []

    errors = (
        db.query(ErrorLog)
        .filter(ErrorLog.employee_id.in_(junior_ids))
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


#----------------- JUNIORS ---------------- #
@router.get("/juniors")
def get_my_juniors(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    junior_ids = get_direct_monitorable_junior_ids(db, user)

    juniors = (
        db.query(User)
        .filter(User.employee_id.in_(junior_ids))
        .all()
    )

    return [
        {
            "employee_id": junior.employee_id,
            "name": junior.name,
            "designation": junior.designation,
            "post": junior.post.title if junior.post else None,
            "level": junior.post.level if junior.post else None
        }
        for junior in juniors
    ]

#------------------ JUNIOR LOGS ---------------- #
@router.get("/logs")
def get_my_junior_logs(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    junior_ids = get_direct_monitorable_junior_ids(db, user)
    return get_logs_for_employee_ids(db, junior_ids)

#------------------ JUNIOR SUMMARY ---------------- #
@router.get("/summary")
def get_my_junior_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    junior_ids = get_direct_monitorable_junior_ids(db, user)
    return get_summary_for_employee_ids(db, junior_ids)

#------------------ JUNIOR METRICS ---------------- #
@router.get("/metrics")
def get_my_junior_metrics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    junior_ids = get_direct_monitorable_junior_ids(db, user)

    return get_metrics_for_employee_ids(
        db,
        junior_ids
    )


@router.get("/errors")
def get_my_junior_errors(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    junior_ids = get_direct_monitorable_junior_ids(db, user)

    return get_errors_for_employee_ids(
        db,
        junior_ids
    )

@router.get("/dashboard/live")
def get_dashboard_live(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return get_dashboard_live_data(
        db,
        user
    )