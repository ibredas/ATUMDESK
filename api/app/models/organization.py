"""
ATUM DESK - Organization Model (Multi-tenant root)
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Organization(Base):
    """Organization entity for multi-tenancy"""
    __tablename__ = "organizations"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Settings and configuration
    settings: Mapped[dict] = mapped_column(JSON, default=dict)
    business_hours: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    holidays: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    allowed_ips: Mapped[Optional[list]] = mapped_column(ARRAY(INET), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization")
    services: Mapped[List["Service"]] = relationship("Service", back_populates="organization")
    tickets: Mapped[List["Ticket"]] = relationship("Ticket", back_populates="organization")
    sla_policies: Mapped[List["SLAPolicy"]] = relationship("SLAPolicy", back_populates="organization")
    custom_fields: Mapped[List["CustomField"]] = relationship("CustomField", back_populates="organization")
    canned_responses: Mapped[List["CannedResponse"]] = relationship("CannedResponse", back_populates="organization")
    kb_categories: Mapped[List["KBCategory"]] = relationship("KBCategory", back_populates="organization")
    kb_articles: Mapped[List["KBArticle"]] = relationship("KBArticle", back_populates="organization")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="organization")
    
    def __repr__(self) -> str:
        return f"<Organization {self.name} ({self.slug})>"
