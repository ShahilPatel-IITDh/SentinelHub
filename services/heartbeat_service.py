from sqlalchemy.orm import Session
from db.models import Machine, ProcessLog
from core.logger import logger
from datetime import datetime


def process_heartbeat(db: Session, data, user_id):

    logger.info(f"Heartbeat received from user {user_id}")

    try:
        # 🔍 Check if machine exists
        machine = db.query(Machine).filter(
            Machine.mac_address == data.mac_address
        ).first()

        # 🆕 Create or update machine
        if not machine:
            machine = Machine(
                mac_address=data.mac_address,
                hostname=data.hostname,
                ip_address=data.ip_address,
                employee_id=user_id
            )
            db.add(machine)
            db.commit()
            db.refresh(machine)
        else:
            # ✅ Update machine info
            machine.hostname = data.hostname
            machine.ip_address = data.ip_address
            db.commit()

        # ✅ SAFE DELETE (keep latest 100 logs)
        old_logs = (
            db.query(ProcessLog)
            .filter(ProcessLog.mac_address == data.mac_address)
            .order_by(ProcessLog.timestamp.desc())
            .offset(100)
            .all()
        )

        for log in old_logs:
            db.delete(log)

        # ✅ Add logs (unique processes only)
        for proc in set(data.processes):
            log = ProcessLog(
                mac_address=data.mac_address,
                employee_id=user_id,
                process_name=proc,
                timestamp=datetime.utcnow()
            )
            db.add(log)

        db.commit()

        logger.info(f"Processed {len(data.processes)} processes")

        return {
            "status": "received",
            "machine": machine.hostname,
            "process_count": len(data.processes)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Heartbeat processing failed: {str(e)}")
        raise