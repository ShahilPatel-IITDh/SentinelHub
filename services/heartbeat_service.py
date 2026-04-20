from sqlalchemy.orm import Session
from db.models import Machine, ProcessLog
from core.logger import logger
from datetime import datetime


def process_heartbeat(db: Session, data, user_id):

    logger.info(f"Heartbeat received from user {user_id}")

    try:
        # Check if machine exists
        machine = db.query(Machine).filter(
            Machine.mac_address == data.mac_address
        ).first()

        # Create machine if not exists
        if not machine:
            machine = Machine(
                mac_address=data.mac_address,
                hostname=data.hostname,
                ip_address=data.ip_address,
                user_id=user_id
            )
            db.add(machine)
            db.commit()
            db.refresh(machine)

            logger.info(f"New machine registered: {machine.hostname}")

        # Insert process logs
        logs_to_add = []
        for proc in data.processes:
            logs_to_add.append(ProcessLog(
                machine_id=machine.id,
                process_name=proc,
                created_at=datetime.utcnow()   # 👈 IMPORTANT
            ))

        db.add_all(logs_to_add)
        db.commit()

        logger.info(f"Processed {len(data.processes)} processes for machine {machine.id}")

        return {
            "status": "received",
            "machine_id": machine.id,
            "process_count": len(data.processes)
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Heartbeat processing failed: {str(e)}")
        raise