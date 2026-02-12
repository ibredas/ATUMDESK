"""
ATUM DESK - User Model with RBAC
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum
from app.db.base import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    CUSTOMER_USER = "customer_user"
    CUSTOMER_ADMIN = "customer_admin"
    AGENT = "agent"
    MANAGER = "manager"
    ADMIN = "admin"


class User(Base):
    """User entity with RBAC"""
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Role-based access control
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.CUSTOMER_USER)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 2FA fields
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    two_factor_backup_codes: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    created_tickets: Mapped[List["Ticket"]] = relationship("Ticket", foreign_keys="Ticket.requester_id", back_populates="requester")
    assigned_tickets: Mapped[List["Ticket"]] = relationship("Ticket", foreign_keys="Ticket.assigned_to", back_populates="assignee")
    accepted_tickets: Mapped[List["Ticket"]] = relationship("Ticket", foreign_keys="Ticket.accepted_by", back_populates="acceptor")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="author")
    attachments: Mapped[List["Attachment"]] = relationship("Attachment", back_populates="uploaded_by_user")
    time_entries: Mapped[List["TimeEntry"]] = relationship("TimeEntry", back_populates="user")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")
    
    # Unique constraint: email within organization
    __table_args__ = (
        # Note: Unique constraint handled in migration for org_id + email
    )
    
    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"
    
    @property
    def is_staff(self) -> bool:
        """Check if user is staff (agent, manager, or admin)"""
        return self.role in [UserRole.AGENT, UserRole.MANAGER, UserRole.ADMIN]
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
