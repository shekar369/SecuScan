from sqlalchemy import Column, String, Text, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from .database import Base

class Website(Base):
    __tablename__ = "websites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, nullable=False, unique=True)
    name = Column(Text)
    created_at = Column(TIMESTAMP, server_default="now()")
    last_scanned_at = Column(TIMESTAMP)

    scans = relationship("ScanRun", back_populates="website", cascade="all, delete-orphan")


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=False)
    started_at = Column(TIMESTAMP, server_default="now()")
    completed_at = Column(TIMESTAMP)
    status = Column(String, CheckConstraint("status IN ('queued', 'running', 'success', 'failed')"))
    report_path = Column(Text)
    parsed_result = Column(JSONB)

    website = relationship("Website", back_populates="scans")
