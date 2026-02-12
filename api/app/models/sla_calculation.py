"""
ATUM DESK - SLA Calculation Model
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class SLACalculation(Base):
    """SLA calculation tracking per ticket"""
    __tablename__ = "sla_calculations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id"), nullable=False, unique=True, index=True
    )
    
    # SLA targets
    first_response_target: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_target: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Actual times
    first_response_actual: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolution_actual: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Breach tracking
    first_response_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    resolution_breached: Mapped[bool] = mapped_column(Boolean, default=False)
    breach_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Calculation details
    business_minutes_elapsed: Mapped[int] = mapped_column(default=0)
    paused_minutes: Mapped[int] = mapped_column(default=0)
    calculation_log: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<SLACalculation ticket={self.ticket_id}>"
    
    @property
    def is_breached(self) -> bool:
        """Check if any SLA has been breached"""
        return self.first_response_breached or self.resolution_breached
