from sqlalchemy.orm import Session
from db.models import ErrorLog, User
from fastapi import HTTPException
from core.logger import logger


def get_manager_errors(db: Session, manager_id: int):
    try:
        # employees under manager
        employees = db.query(User.employee_id).filter(
            User.reporting_officer_id == manager_id
        ).all()

        employee_ids = [e.employee_id for e in employees]
        employee_ids.append(manager_id)

        errors = (
            db.query(ErrorLog)
            .filter(ErrorLog.employee_id.in_(employee_ids))
            .order_by(ErrorLog.timestamp.desc())
            .limit(200)
            .all()
        )

        return [
            {
                "employee_id": e.employee_id,
                "mac_address": e.mac_address,
                "error_type": e.error_type,
                "message": e.message,
                "severity": e.severity,
                "timestamp": e.timestamp
            }
            for e in errors
        ]

    except Exception as e:
        logger.error(f"[ERROR_SERVICE] {str(e)}")
        raise HTTPException(500, "Error fetching error logs")
    
# Maintain the errors Log 

def get_errors_for_employee_ids(
    db,
    employee_ids,
    limit: int = 100
):
    if not employee_ids:
        return []

    errors = (
        db.query(ErrorLog)
        .filter(ErrorLog.employee_id.in_(employee_ids))
        .order_by(ErrorLog.timestamp.desc())
        .limit(limit)
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