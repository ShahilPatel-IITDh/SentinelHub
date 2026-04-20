from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import SessionLocal
from schemas.schemas import RegisterUser, LoginUser
from services.auth_service import register_user, login_user

router = APIRouter(prefix="/api/auth")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
def register(user: RegisterUser, db: Session = Depends(get_db)):
    return register_user(db, user)


@router.post("/login")
def login(data: LoginUser, db: Session = Depends(get_db)):
    return login_user(db, data)