from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload

from db.database import SessionLocal
from db.models import User
from core.security import decode_token

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)):
    token = credentials.credentials

    try:
        employee_id = decode_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).options(joinedload(User.post)).filter(User.employee_id == employee_id).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def require_hierarchy_admin(user: User = Depends(get_current_user)):
    if not user.post or not user.post.can_manage_hierarchy:
        raise HTTPException(
            status_code=403,
            detail="Only hierarchy administrators can perform this action"
        )

    return user