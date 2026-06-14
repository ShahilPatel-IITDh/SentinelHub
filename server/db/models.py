from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base


# ---------------- POST / HIERARCHY ---------------- #

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False, index=True)
    level = Column(Integer, nullable=False, index=True)

    
    can_monitor = Column(Integer, default=0)          
    can_manage_hierarchy = Column(Integer, default=0) 

    users = relationship("User", back_populates="post")

# ---------------- USER ---------------- #

class User(Base):
    __tablename__ = "users"

    employee_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    
    # New hierarchy-based post
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True, index=True)

    reporting_officer_id = Column(
        Integer,
        ForeignKey("users.employee_id"),
        nullable=True,
        index=True
    )

    manager = relationship(
        "User",
        remote_side=[employee_id],
        backref="subordinates"
    )
    
    post = relationship("Post", back_populates="users")
    
    machines = relationship(
        "Machine",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ---------------- MACHINE ---------------- #

class Machine(Base):
    __tablename__ = "machines"

    mac_address = Column(String, primary_key=True, index=True)
    hostname = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)

    employee_id = Column(Integer, ForeignKey("users.employee_id"), index=True)

    last_seen = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="machines")
    logs = relationship(
        "ProcessLog",
        back_populates="machine",
        cascade="all, delete-orphan"
    )


# ---------------- PROCESS LOG ---------------- #

class ProcessLog(Base):
    __tablename__ = "process_logs"

    id = Column(Integer, primary_key=True, index=True)

    mac_address = Column(String, ForeignKey("machines.mac_address"), index=True)
    employee_id = Column(Integer, ForeignKey("users.employee_id"), index=True)

    process_name = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    machine = relationship("Machine", back_populates="logs")


# ---------------- SYSTEM METRICS ---------------- #

class SystemMetrics(Base):
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)

    mac_address = Column(String, index=True)
    employee_id = Column(Integer, index=True)

    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# ---------------- ERROR LOGS ---------------- #

class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)

    mac_address = Column(String, index=True, nullable=False)
    employee_id = Column(Integer, index=True, nullable=False)

    error_type = Column(String, nullable=False, index=True)
    # Example: HIGH_CPU, HIGH_MEMORY

    message = Column(String, nullable=False)

    severity = Column(String, nullable=False, default="LOW")
    # Use only: LOW / MEDIUM / HIGH

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)