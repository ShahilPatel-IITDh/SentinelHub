from sqlalchemy.orm import Session
from db.models import User, Machine, ProcessLog


def get_manager_logs(db: Session, manager_id: int):

    # Get employees under manager
    juniors = db.query(User).filter(
        User.reporting_officer_id == manager_id
    ).all()

    junior_ids = [j.id for j in juniors]

    # Get machines
    machines = db.query(Machine).filter(
        Machine.user_id.in_(junior_ids)
    ).all()

    machine_map = {m.id: m for m in machines}
    machine_ids = list(machine_map.keys())

    # Get logs
    logs = db.query(ProcessLog).filter(
        ProcessLog.machine_id.in_(machine_ids)
    ).all()

    # Format output
    result = []

    for log in logs:
        machine = machine_map.get(log.machine_id)

        result.append({
            "machine": machine.hostname,
            "ip": machine.ip_address,
            "process": log.process_name,
            "timestamp": log.created_at
        })

    return result