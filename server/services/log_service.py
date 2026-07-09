from sqlalchemy.orm import Session
from db.models import ProcessLog, Machine, User
from core.logger import logger
from fastapi import HTTPException


def get_manager_logs(db: Session, manager_id: int, limit: int = 100):
    try:
        # ---------------- EMPLOYEES ---------------- #
        employees = db.query(User.employee_id).filter(
            User.reporting_officer_id == manager_id
        ).all()

        employee_ids = [e.employee_id for e in employees]
        employee_ids.append(manager_id)

        # ---------------- LOG QUERY ---------------- #
        logs = (
            db.query(ProcessLog, Machine)
            .join(Machine, ProcessLog.mac_address == Machine.mac_address)
            .filter(ProcessLog.employee_id.in_(employee_ids))
            .order_by(ProcessLog.timestamp.desc())
            .limit(limit)
            .all()
        )

        if not logs:
            return []

        # ---------------- FORMAT ---------------- #
        result = [
            {
                "employee_id": log.employee_id,
                "process_name": log.process_name,
                "machine_mac": machine.mac_address,
                "hostname": machine.hostname,
                "ip_address": machine.ip_address,
                "timestamp": log.timestamp
            }
            for log, machine in logs
        ]

        logger.info(
            f"[LOG_SERVICE] {len(result)} logs fetched for manager {manager_id}"
        )

        return result

    except Exception as e:
        logger.error(f"[LOG_SERVICE] Error: {str(e)}")
        raise HTTPException(500, "Internal server error")
    

def get_logs_for_employee_ids(db, employee_ids, limit: int = 500):
    if not employee_ids:
        return []

    logs = (
        db.query(ProcessLog, Machine)
        .join(Machine, ProcessLog.mac_address == Machine.mac_address)
        .filter(ProcessLog.employee_id.in_(employee_ids))
        .order_by(ProcessLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "employee_id": log.employee_id,
            "process_name": log.process_name,
            "mac_address": log.mac_address,
            "hostname": machine.hostname,
            "ip_address": machine.ip_address,
            "timestamp": log.timestamp
        }
        for log, machine in logs
    ]

    