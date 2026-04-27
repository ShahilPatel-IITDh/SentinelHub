from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


# ---------------- USER ---------------- #

class User(Base):
    __tablename__ = "users"

    employee_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    designation = Column(String)

    # ✅ FIXED: self-referencing foreign key
    reporting_officer_id = Column(
        Integer,
        ForeignKey("users.employee_id"),
        nullable=True
    )

    # ✅ Relationships (self-reference)
    manager = relationship(
        "User",
        remote_side=[employee_id],
        backref="subordinates"
    )

    # ✅ Relationship with machines
    machines = relationship("Machine", back_populates="user")


# ---------------- MACHINE ---------------- #

class Machine(Base):
    __tablename__ = "machines"

    mac_address = Column(String, primary_key=True, index=True)
    hostname = Column(String)
    ip_address = Column(String)

    employee_id = Column(Integer, ForeignKey("users.employee_id"))

    user = relationship("User", back_populates="machines")
    logs = relationship("ProcessLog", back_populates="machine")


# ---------------- PROCESS LOG ---------------- #

class ProcessLog(Base):
    __tablename__ = "process_logs"

    id = Column(Integer, primary_key=True, index=True)

    mac_address = Column(String, ForeignKey("machines.mac_address"))
    employee_id = Column(Integer, ForeignKey("users.employee_id"))

    process_name = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    machine = relationship("Machine", back_populates="logs")