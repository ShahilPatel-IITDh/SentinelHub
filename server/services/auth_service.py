from sqlalchemy.orm import Session
from db.models import User
from core.security import hash_password, verify_password, create_token
from core.logger import logger
from fastapi import HTTPException, status


# ---------------- REGISTER ---------------- #

def register_user(db: Session, user):

    logger.info(f"Register attempt for employee_id={user.employee_id}")

    try:
        employee_id = int(user.employee_id)

        # Remove duplicate password validation (handled in routes)

        existing = db.query(User).filter(
            User.employee_id == employee_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="User already exists"
            )

        # ✅ Allow employee without manager
        if user.reporting_officer_id is not None:
            manager = db.query(User).filter(
                User.employee_id == user.reporting_officer_id
            ).first()

            if not manager:
                logger.warning(
                    f"[REGISTER] Manager {user.reporting_officer_id} not found for user {employee_id}"
                )

        new_user = User(
            name=user.name,
            employee_id=employee_id,
            password=hash_password(str(user.password)),
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
        raise HTTPException(500, "Internal server error")


# ---------------- LOGIN ---------------- #

def login_user(db: Session, data):

    logger.info(f"Login attempt for employee_id={data.employee_id}")

    try:
        employee_id = int(data.employee_id)

        user = db.query(User).filter(
            User.employee_id == employee_id
        ).first()

        if not user:
            raise HTTPException(404, "User not found")

        if not verify_password(str(data.password), user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

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
        raise HTTPException(500, "Internal server error")


# ---------------- ASSIGN MANAGER ---------------- #

def assign_manager(db: Session, employee_id: int, manager_id: int):
    try:
        employee = db.query(User).filter(
            User.employee_id == employee_id
        ).first()

        if not employee:
            raise HTTPException(404, "Employee not found")

        manager = db.query(User).filter(
            User.employee_id == manager_id
        ).first()

        if not manager:
            raise HTTPException(404, "Manager not found")

        # ✅ Ensure manager role
        if manager.designation.lower() != "manager":
            raise HTTPException(
                400,
                "Assigned user is not a manager"
            )

        employee.reporting_officer_id = manager_id
        db.commit()

        logger.info(f"[ASSIGN] {employee_id} → manager {manager_id}")

        return {"status": "success", "message": "Manager assigned"}

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"[ASSIGN ERROR] {str(e)}")
        raise HTTPException(500, "Internal server error")


# ---------------- UPDATE DESIGNATION ---------------- #

def update_designation(db: Session, employee_id: int, designation: str):
    try:
        user = db.query(User).filter(
            User.employee_id == employee_id
        ).first()

        if not user:
            raise HTTPException(404, "User not found")

        old_designation = user.designation

        # Prevent demotion breaking hierarchy
        if designation.lower() != "manager":
            subordinates = db.query(User).filter(
                User.reporting_officer_id == employee_id
            ).first()

            if subordinates:
                raise HTTPException(
                    400,
                    "Cannot demote user with active subordinates"
                )

        user.designation = designation
        db.commit()

        logger.info(
            f"[PROMOTION] {employee_id}: {old_designation} → {designation}"
        )

        return {
            "status": "success",
            "message": "Designation updated"
        }

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"[PROMOTION ERROR] {str(e)}")
        raise HTTPException(500, "Internal server error")