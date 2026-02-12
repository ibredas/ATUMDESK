"""
ATUM DESK - SLA Policy Model
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SLAPolicy(Base):
    """SLA policy definitions with business hours"""
    __tablename__ = "sla_policies"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    
    # Policy details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Response times (in minutes)
    response_time_low: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_medium: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_high: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    response_time_urgent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Resolution times (in minutes)
    resolution_time_low: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolution_time_medium: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolution_time_high: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    resolution_time_urgent: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Business hours configuration
    business_hours_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    business_hours_schedule: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    
    # Escalation rules
    escalation_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    escalation_rules: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="sla_policies")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="sla_policy")
    
    def __repr__(self) -> str:
        return f"<SLAPolicy {self.name}>"
    
    def get_response_time(self, priority: str) -> Optional[int]:
        """Get response time for a priority level"""
        mapping = {
            "low": self.response_time_low,
            "medium": self.response_time_medium,
            "high": self.response_time_high,
            "urgent": self.response_time_urgent,
        }
        return mapping.get(priority.lower())
    
    def get_resolution_time(self, priority: str) -> Optional[int]:
        """Get resolution time for a priority level"""
        mapping = {
            "low": self.resolution_time_low,
            "medium": self.resolution_time_medium,
            "high": self.resolution_time_high,
            "urgent": self.resolution_time_urgent,
        }
        return mapping.get(priority.lower())
