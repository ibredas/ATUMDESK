"""
ATUM DESK - Ticket Model (Core Entity)
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
import enum
from app.db.base import Base


class TicketStatus(str, enum.Enum):
    """Ticket status workflow"""
    NEW = "new"
    ACCEPTED = "accepted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, enum.Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Ticket(Base):
    """Core ticket entity"""
    __tablename__ = "tickets"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    
    # Relationships
    requester_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    service_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("services.id"), nullable=True
    )
    
    # Ticket content
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status workflow
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus), nullable=False, default=TicketStatus.NEW, index=True
    )
    
    # Assignment
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True
    )
    accepted_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    accepted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Priority & categorization
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM, index=True
    )
    
    # SLA tracking
    sla_policy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("sla_policies.id"), nullable=True
    )
    sla_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sla_due_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    sla_paused_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sla_paused_duration: Mapped[int] = mapped_column(default=0)  # seconds
    
    # Ticket relationships
    parent_ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tickets.id"), nullable=True
    )
    is_duplicate_of: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("tickets.id"), nullable=True
    )
    
    # AI triage (optional)
    ai_suggested_category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ai_suggested_priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    ai_confidence_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # RAG Embeddings (pgvector)
    # Using 768 dimensions for nomic-embed-text
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="tickets")
    requester: Mapped["User"] = relationship("User", foreign_keys=[requester_id], back_populates="created_tickets")
    service: Mapped[Optional["Service"]] = relationship("Service", back_populates="tickets")
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    acceptor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[accepted_by], back_populates="accepted_tickets")
    sla_policy: Mapped[Optional["SLAPolicy"]] = relationship("SLAPolicy", back_populates="tickets")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="ticket", order_by="Comment.created_at")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="ticket")
    time_entries: Mapped[List["TimeEntry"]] = relationship("TimeEntry", back_populates="ticket")
    custom_field_values: Mapped[List["CustomFieldValue"]] = relationship("CustomFieldValue", back_populates="ticket")
    csat_surveys: Mapped[List["CSATSurvey"]] = relationship("CSATSurvey", back_populates="ticket")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_tickets_org_status', 'organization_id', 'status'),
        Index('ix_tickets_org_created', 'organization_id', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Ticket {self.id} - {self.subject[:50]}>"
    
    @property
    def is_open(self) -> bool:
        """Check if ticket is still open"""
        return self.status not in [TicketStatus.CLOSED, TicketStatus.CANCELLED]
    
    @property
    def is_waiting(self) -> bool:
        """Check if ticket is waiting for customer"""
        return self.status == TicketStatus.WAITING_CUSTOMER
