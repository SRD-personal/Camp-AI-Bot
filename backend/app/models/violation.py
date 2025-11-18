"""
Violation logging model (append-only)
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base


class ViolationSeverity(str, enum.Enum):
    """Violation severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ViolationLog(Base):
    """Tamper-proof violation log (append-only)"""
    
    __tablename__ = "violation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    violation_rule = Column(String(255), nullable=False)
    severity = Column(SQLEnum(ViolationSeverity), nullable=False)
    
    original_message = Column(Text, nullable=False)
    violation_details = Column(JSON, nullable=True)
    
    # Immutable timestamp
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    message = relationship("Message", back_populates="violations")
    sender = relationship("User")
    
    def __repr__(self):
        return f"<ViolationLog {self.violation_rule} ({self.severity})>"
    
    def to_dict(self):
        """Convert violation to dictionary"""
        return {
            "id": str(self.id),
            "message_id": str(self.message_id) if self.message_id else None,
            "sender_id": str(self.sender_id),
            "violation_rule": self.violation_rule,
            "severity": self.severity.value,
            "original_message": self.original_message,
            "violation_details": self.violation_details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
