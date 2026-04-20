from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from db.database import SessionLocal
from schemas.schemas import Heartbeat
from services.heartbeat_service import process_heartbeat
from services.log_service import get_manager_logs   # ✅ NEW

from core.security import decode_token

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

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    return decode_token(token)


# ---------------- HEARTBEAT ---------------- #

@router.post("/heartbeat")
def heartbeat(
    data: Heartbeat,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    return process_heartbeat(db, data, user_id)


# ---------------- LOGS (UPDATED) ---------------- #

@router.get("/logs/{manager_id}")
def get_logs(
    manager_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    # 🔐 Security check
    if user_id != manager_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # ✅ USE NEW SERVICE (THIS FIXES YOUR ISSUE)
    return get_manager_logs(db, manager_id)