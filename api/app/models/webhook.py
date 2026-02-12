"""
ATUM DESK - Webhook Model
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Webhook(Base):
    """Webhook configuration for outbound events"""
    __tablename__ = "webhooks"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    
    # Target
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False) # For HMAC signature
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Configuration
    event_types: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False) # e.g. ["ticket.created", "ticket.updated"]
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Metadata
    created_by_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_failure_reason: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    failure_count: Mapped[int] = mapped_column(default=0)
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization")
    created_by: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<Webhook {self.id} - {self.url}>"
