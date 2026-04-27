from sqlalchemy.orm import Session
from db.models import Machine, ProcessLog, User
from datetime import datetime, timedelta


def get_summary(db: Session, manager_id: int):

    # Step 1: Get employees under manager
    employees = db.query(User).filter(
        User.reporting_officer_id == manager_id
    ).all()

    employee_ids = [e.employee_id for e in employees]
    employee_ids.append(manager_id)  # include manager

    # Step 2: Machines
    machines = db.query(Machine).filter(
        Machine.employee_id.in_(employee_ids)
    ).all()

    total_machines = len(machines)

    # Step 3: Active vs inactive
    now = datetime.utcnow()
    active_threshold = now - timedelta(minutes=5)

    active = 0
    for m in machines:
        if m.last_seen and m.last_seen > active_threshold:
            active += 1

    inactive = total_machines - active

    # Step 4: Process count
    total_processes = db.query(ProcessLog).filter(
        ProcessLog.employee_id.in_(employee_ids)
    ).count()

    return {
        "total_machines": total_machines,
        "active_machines": active,
        "inactive_machines": inactive,
        "total_processes": total_processes
    }