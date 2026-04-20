from sqlalchemy.orm import Session
from db.models import User
from core.security import hash_password, verify_password, create_token
from core.logger import logger
from fastapi import HTTPException, status


# ---------------- REGISTER ---------------- #

def register_user(db: Session, user):

    logger.info(f"Register attempt for employee_id={user.employee_id}")

    try:
        # Check if user already exists
        existing = db.query(User).filter(
            User.employee_id == user.employee_id
        ).first()

        if existing:
            logger.warning("User already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists"
            )

        # Optional: validate reporting officer (important for hierarchy)
        if user.reporting_officer_id != 0:
            manager = db.query(User).filter(
                User.id == user.reporting_officer_id
            ).first()

            if not manager:
                raise HTTPException(
                    status_code=400,
                    detail="Reporting officer not found"
                )

        # Create user
        new_user = User(
            name=user.name,
            employee_id=user.employee_id,
            password=hash_password(user.password),
            designation=user.designation,
            reporting_officer_id=user.reporting_officer_id
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(f"User created successfully id={new_user.id}")

        return {
            "status": "success",
            "message": "User created",
            "user_id": new_user.id
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
        user = db.query(User).filter(
            User.employee_id == data.employee_id
        ).first()

        if not user:
            logger.warning("User not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if not verify_password(data.password, user.password):
            logger.warning("Invalid password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Generate token
        token = create_token(user.id)

        logger.info(f"Login successful user_id={user.id}")

        return {
            "status": "success",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
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