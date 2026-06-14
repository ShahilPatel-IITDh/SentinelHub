from sqlalchemy.orm import Session
from db.models import Machine, ProcessLog, User
from datetime import datetime, timedelta
from core.logger import logger
from fastapi import HTTPException


def get_summary(db: Session, manager_id: int):
    try:
        # Step 1: Get employees under manager
        employees = db.query(User.employee_id).filter(
            User.reporting_officer_id == manager_id
        ).all()

        employee_ids = [e.employee_id for e in employees]
        employee_ids.append(manager_id)

        # Step 2: Machines
        machines = db.query(Machine).filter(
            Machine.employee_id.in_(employee_ids)
        ).all()

        total_machines = len(machines)

        # Step 3: Active vs inactive
        now = datetime.utcnow()
        active_threshold = now - timedelta(minutes=5)

        active = sum(
            1 for m in machines
            if m.last_seen and m.last_seen > active_threshold
        )

        inactive = total_machines - active

        # Step 4: Process count
        total_processes = db.query(ProcessLog).filter(
            ProcessLog.employee_id.in_(employee_ids)
        ).count()

        result = {
            "total_machines": total_machines,
            "active_machines": active,
            "inactive_machines": inactive,
            "total_processes": total_processes
        }

        logger.info(f"[SUMMARY_SERVICE] Summary generated for manager {manager_id}")

        return result

    except Exception as e:
        logger.error(f"[SUMMARY_SERVICE] Error: {str(e)}")
        raise HTTPException(500, "Internal server error")
    

# Additional helper for summary endpoint to get summary for any list of employee IDs (used by hierarchy service) #

def get_summary_for_employee_ids(db, employee_ids):
    if not employee_ids:
        return {
            "total_juniors": 0,
            "total_machines": 0,
            "active_machines": 0,
            "inactive_machines": 0,
            "total_processes": 0
        }

    active_threshold = datetime.utcnow() - timedelta(minutes=5)

    total_machines = (
        db.query(Machine)
        .filter(Machine.employee_id.in_(employee_ids))
        .count()
    )

    active_machines = (
        db.query(Machine)
        .filter(
            Machine.employee_id.in_(employee_ids),
            Machine.last_seen >= active_threshold
        )
        .count()
    )

    total_processes = (
        db.query(ProcessLog)
        .filter(ProcessLog.employee_id.in_(employee_ids))
        .count()
    )

    return {
        "total_juniors": len(employee_ids),
        "total_machines": total_machines,
        "active_machines": active_machines,
        "inactive_machines": total_machines - active_machines,
        "total_processes": total_processes
    }