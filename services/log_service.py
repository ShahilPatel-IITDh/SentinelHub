from sqlalchemy.orm import Session
from db.models import ProcessLog, Machine, User
from core.logger import logger


def get_manager_logs(db: Session, manager_id: int):
    try:
        # ✅ Step 1: get all employees under manager
        employees = db.query(User).filter(
            User.reporting_officer_id == manager_id
        ).all()

        employee_ids = [emp.employee_id for emp in employees]

        # ✅ include manager himself
        employee_ids.append(manager_id)

        # ✅ Step 2: fetch logs
        logs = (
            db.query(ProcessLog, Machine)
            .join(Machine, ProcessLog.mac_address == Machine.mac_address)
            .filter(ProcessLog.employee_id.in_(employee_ids))
            .order_by(ProcessLog.timestamp.desc())
            .all()
        )

        result = []

        for log, machine in logs:
            result.append({
                "employee_id": log.employee_id,   # 🔥 important
                "process_name": log.process_name,
                "machine_mac": machine.mac_address,
                "hostname": machine.hostname,
                "ip_address": machine.ip_address,
                "timestamp": log.timestamp
            })

        logger.info(f"Fetched {len(result)} logs for manager {manager_id}")

        return result

    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise