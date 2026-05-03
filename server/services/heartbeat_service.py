from sqlalchemy.orm import Session
from db.models import Machine, ProcessLog, SystemMetrics, ErrorLog
from core.logger import logger
from datetime import datetime, timedelta
from fastapi import HTTPException


# ---------------- HELPER: PREVENT ERROR SPAM ---------------- #

def log_error_once(db, mac, user_id, error_type, message, severity):
    """Avoid duplicate error logs within 30 seconds"""

    try:
        recent = db.query(ErrorLog).filter(
            ErrorLog.mac_address == mac,
            ErrorLog.error_type == error_type,
            ErrorLog.timestamp > datetime.utcnow() - timedelta(seconds=30)
        ).first()

        if not recent:
            db.add(ErrorLog(
                mac_address=mac,
                employee_id=user_id,
                error_type=error_type,
                message=message,
                severity=severity,
                timestamp=datetime.utcnow()
            ))

    except Exception as e:
        logger.error(f"[ERROR_LOGGING_FAILED] {str(e)}")


# ---------------- MAIN HEARTBEAT ---------------- #

def process_heartbeat(db: Session, data, user_id):

    logger.info(f"Heartbeat received from user {user_id}")

    try:
        # ---------------- MACHINE ---------------- #
        machine = db.query(Machine).filter(
            Machine.mac_address == data.mac_address
        ).first()

        if not machine:
            machine = Machine(
                mac_address=data.mac_address,
                hostname=data.hostname,
                ip_address=data.ip_address,
                employee_id=user_id,
                last_seen=datetime.utcnow()
            )
            db.add(machine)
        else:
            machine.hostname = data.hostname
            machine.ip_address = data.ip_address
            machine.last_seen = datetime.utcnow()

        # ---------------- PROCESS LOGS ---------------- #
        if not data.processes:
            logger.warning("No processes received")
            return {"status": "no_processes"}

        for proc in set(data.processes):
            db.add(ProcessLog(
                mac_address=data.mac_address,
                employee_id=user_id,
                process_name=proc,
                timestamp=datetime.utcnow()
            ))

        # ---------------- METRICS ---------------- #
        cpu = max(0, min(data.cpu_percent, 100))
        mem = max(0, min(data.memory_percent, 100))
        disk = max(0, min(data.disk_percent, 100))

        db.add(SystemMetrics(
            mac_address=data.mac_address,
            employee_id=user_id,
            cpu_percent=cpu,
            memory_percent=mem,
            disk_percent=disk
        ))

        # ---------------- SMART ALERTS ---------------- #

        # 🔥 High CPU (only if system actually stressed)
        if cpu > 85 and mem > 50:
            log_error_once(
                db,
                data.mac_address,
                user_id,
                "HIGH_CPU",
                f"CPU usage high: {cpu}%",
                "HIGH"
            )

        # 🔥 High Memory
        if mem > 85:
            log_error_once(
                db,
                data.mac_address,
                user_id,
                "HIGH_MEMORY",
                f"Memory usage high: {mem}%",
                "HIGH"
            )

        # 🟠 High Disk
        if disk > 90:
            log_error_once(
                db,
                data.mac_address,
                user_id,
                "HIGH_DISK",
                f"Disk usage critical: {disk}%",
                "MEDIUM"
            )

        # ---------------- COMMIT ---------------- #
        db.commit()

        logger.info(f"[METRICS] CPU={cpu}% | MEM={mem}% | DISK={disk}%")
        logger.info(f"Processed {len(data.processes)} processes")

        return {
            "status": "received",
            "machine": machine.hostname,
            "process_count": len(data.processes)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Heartbeat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")