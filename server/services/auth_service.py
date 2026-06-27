from sqlalchemy.orm import Session
from db.models import User, Post
from core.security import hash_password, verify_password, create_token
from core.logger import logger
from fastapi import HTTPException, status
from services.hierarchy_service import validate_reporting_assignment

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

        reporting_officer_id = user.reporting_officer_id
        if reporting_officer_id == 0:
            reporting_officer_id = None

        # Allow employee without manager
        if reporting_officer_id is not None:
            manager = db.query(User).filter(
                User.employee_id == reporting_officer_id
            ).first()

            if not manager:
                logger.warning(
                    f"[REGISTER] Manager {reporting_officer_id} not found for user {employee_id}"
                )

        new_user = User(
            name=user.name,
            employee_id=employee_id,
            password=hash_password(str(user.password)),
            designation=user.designation,
            post_id=user.post_id,
            reporting_officer_id=reporting_officer_id,
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

        # Ensure manager role
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
    






#----------------- CREATE POST ---------------- for hierarchy#
def create_post(db, data):
    existing = db.query(Post).filter(Post.title == data.title).first()

    if existing:
        raise HTTPException(status_code=400, detail="Post already exists")

    post = Post(
        title=data.title,
        level=data.level,
        can_monitor=1 if data.can_monitor else 0,
        can_manage_hierarchy=1 if data.can_manage_hierarchy else 0
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    return {
        "status": "success",
        "message": "Post created successfully",
        "post_id": post.id
    }    

#----------------- UPDATE USER POST ---------------- for hierarchy#
def update_user_post(db, employee_id: int, post_id: int):
    user = db.query(User).filter(User.employee_id == employee_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    user.post_id = post.id

    # Backward compatibility: old project still uses designation
    user.designation = post.title

    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "User post updated successfully"
    }

#----------------- ASSIGN REPORTING OFFICER ---------------- for hierarchy#
def assign_reporting_officer(db, employee_id: int, reporting_officer_id: int):
    employee = db.query(User).filter(User.employee_id == employee_id).first()
    officer = db.query(User).filter(User.employee_id == reporting_officer_id).first()

    validate_reporting_assignment(employee, officer)

    employee.reporting_officer_id = reporting_officer_id

    db.commit()
    db.refresh(employee)

    return {
        "status": "success",
        "message": "Reporting officer assigned successfully"
    }