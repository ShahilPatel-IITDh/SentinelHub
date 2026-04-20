from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    employee_id = Column(String, unique=True)
    password = Column(String)
    designation = Column(String)
    reporting_officer_id = Column(Integer)


class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True)
    mac_address = Column(String, unique=True)
    hostname = Column(String)
    ip_address = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))


from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

class ProcessLog(Base):
    __tablename__ = "process_logs"

    id = Column(Integer, primary_key=True, index=True)
    machine_id = Column(Integer, ForeignKey("machines.id"))
    process_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)