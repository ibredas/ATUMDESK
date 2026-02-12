"""
ATUM DESK - Service Model (Ticket Categories)
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Service(Base):
    """Service/Category for ticket classification"""
    __tablename__ = "services"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    
    # Service details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_priority: Mapped[str] = mapped_column(String(20), default="medium")
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="services")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="service")
    
    def __repr__(self) -> str:
        return f"<Service {self.name}>"
