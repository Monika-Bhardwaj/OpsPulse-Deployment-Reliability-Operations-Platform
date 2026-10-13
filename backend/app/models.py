from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship
from .db import Base


def _now():
    return datetime.now(timezone.utc)


class Environment(Base):
    __tablename__ = "environments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, default="", nullable=False, server_default="")
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    deployments = relationship("Deployment", back_populates="environment")


class Deployment(Base):
    __tablename__ = "deployments"
    __table_args__ = (Index("ix_deployments_status", "status"),)

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(200), nullable=False)
    version = Column(String(100), nullable=False)
    environment_id = Column(Integer, ForeignKey("environments.id"), nullable=True)
    status = Column(String(30), default="PENDING", nullable=False)
    deployed_by = Column(String(120), default="system", nullable=False)
    notes = Column(Text, default="", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)

    environment = relationship("Environment", back_populates="deployments")


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (Index("ix_incidents_status", "status"),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="", nullable=False)
    severity = Column(String(20), default="MEDIUM", nullable=False)
    status = Column(String(30), default="OPEN", nullable=False)
    affected_service = Column(String(200), default="", nullable=False)
    owner = Column(String(120), default="Unassigned", nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=_now, onupdate=_now, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
