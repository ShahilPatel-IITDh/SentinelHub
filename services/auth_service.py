from sqlalchemy.orm import Session
from db.models import User
from core.security import hash_password, verify_password, create_token
from core.logger import logger
from fastapi import HTTPException, status


# ---------------- REGISTER ---------------- #

def register_user(db: Session, user):

    logger.info(f"Register attempt for employee_id={user.employee_id}")

    try:
        # ✅ Ensure employee_id is int
        try:
            employee_id = int(user.employee_id)
        except:
            raise HTTPException(
                status_code=400,
                detail="employee_id must be an integer"
            )

        # ✅ Password validation
        plain_password = str(user.password)

        if len(plain_password) < 6:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 6 characters"
            )

        if len(plain_password.encode("utf-8")) > 72:
            raise HTTPException(
                status_code=400,
                detail="Password too long (max 72 bytes)"
            )

        # ✅ Check if user already exists
        existing = db.query(User).filter(
            User.employee_id == employee_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        # ✅ Validate reporting officer (FIXED)
        if user.reporting_officer_id:
            manager = db.query(User).filter(
                User.employee_id == user.reporting_officer_id
            ).first()

            if not manager:
                raise HTTPException(
                    status_code=400,
                    detail="Reporting officer not found"
                )

        # ✅ Create user
        new_user = User(
            name=user.name,
            employee_id=employee_id,
            password=hash_password(plain_password),
            designation=user.designation,
            reporting_officer_id=user.reporting_officer_id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User created: {new_user.employee_id}")

        return {
            "status": "success",
            "message": "User created",
            "user_id": new_user.employee_id
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )


# ---------------- LOGIN ---------------- #

def login_user(db: Session, data):

    logger.info(f"Login attempt for employee_id={data.employee_id}")

    try:
        # ✅ Ensure employee_id is int
        try:
            employee_id = int(data.employee_id)
        except:
            raise HTTPException(
                status_code=400,
                detail="employee_id must be an integer"
            )

        user = db.query(User).filter(
            User.employee_id == employee_id
        ).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not verify_password(str(data.password), user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # ✅ Generate token
        token = create_token(user.employee_id)

        logger.info(f"Login successful: {user.employee_id}")

        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "employee_id": user.employee_id,
                "name": user.name,
                "designation": user.designation
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )