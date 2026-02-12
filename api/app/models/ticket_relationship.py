"""
ATUM DESK - Ticket Relationship Model
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import enum
from app.db.base import Base


class RelationshipType(str, enum.Enum):
    """Types of ticket relationships"""
    PARENT = "parent"
    CHILD = "child"
    DUPLICATE = "duplicate"
    RELATED = "related"
    BLOCKED_BY = "blocked_by"
    BLOCKS = "blocks"


class TicketRelationship(Base):
    """Relationships between tickets"""
    __tablename__ = "ticket_relationships"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id"), nullable=False, index=True
    )
    target_ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id"), nullable=False, index=True
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        String(50), nullable=False
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    
    # Unique constraint: source + target + type
    __table_args__ = (
        Index('ix_ticket_relationships_unique', 
              'source_ticket_id', 'target_ticket_id', 'relationship_type', 
              unique=True),
    )
    
    def __repr__(self) -> str:
        return f"<TicketRelationship {self.source_ticket_id} {self.relationship_type} {self.target_ticket_id}>"
