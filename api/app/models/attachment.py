"""
ATUM DESK - Attachment Model
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Attachment(Base):
    """File attachments for tickets and comments"""
    __tablename__ = "attachments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id"), nullable=False, index=True
    )
    comment_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("comments.id"), nullable=True, index=True
    )
    
    # File details
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)  # SHA-256
    
    # Upload tracking
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    last_accessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    
    # Relationships
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="attachments")
    comment: Mapped[Optional["Comment"]] = relationship("Comment", back_populates="attachments")
    uploaded_by_user: Mapped["User"] = relationship("User", back_populates="attachments")
    
    def __repr__(self) -> str:
        return f"<Attachment {self.original_filename}>"
