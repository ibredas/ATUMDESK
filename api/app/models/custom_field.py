"""
ATUM DESK - Custom Field Model
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.base import Base


class FieldType(str, enum.Enum):
    """Custom field types"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    MULTISELECT = "multiselect"


class CustomField(Base):
    """Custom field definitions"""
    __tablename__ = "custom_fields"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    
    # Field definition
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    field_type: Mapped[FieldType] = mapped_column(String(50), nullable=False)
    options: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)  # For dropdown/multiselect
    
    # Settings
    is_required: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="custom_fields")
    values: Mapped[List["CustomFieldValue"]] = relationship("CustomFieldValue", back_populates="custom_field")
    
    def __repr__(self) -> str:
        return f"<CustomField {self.name} ({self.field_type})>"


class CustomFieldValue(Base):
    """Custom field values for tickets"""
    __tablename__ = "custom_field_values"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    custom_field_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("custom_fields.id"), nullable=False, index=True
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id"), nullable=False, index=True
    )
    
    # Value stored as JSON for flexibility
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Unique constraint: one value per field per ticket
    __table_args__ = (
        # Note: Unique constraint in migration
    )
    
    # Relationships
    custom_field: Mapped["CustomField"] = relationship("CustomField", back_populates="values")
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="custom_field_values")
    
    def __repr__(self) -> str:
        return f"<CustomFieldValue field={self.custom_field_id} ticket={self.ticket_id}>"
