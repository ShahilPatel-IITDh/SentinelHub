from db.models import SystemMetrics
from db.models import ErrorLog

def get_metrics_for_employee_ids(
    db,
    employee_ids,
    limit: int = 500
):
    if not employee_ids:
        return []

    metrics = (
        db.query(SystemMetrics)
        .filter(SystemMetrics.employee_id.in_(employee_ids))
        .order_by(SystemMetrics.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "mac_address": m.mac_address,
            "employee_id": m.employee_id,
            "cpu_percent": m.cpu_percent,
            "memory_percent": m.memory_percent,
            "disk_percent": m.disk_percent,
            "timestamp": m.timestamp
        }
        for m in metrics
    ]

