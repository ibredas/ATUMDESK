"""
ATUM DESK - Knowledge Base Category Model
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class KBCategory(Base):
    """Knowledge base category organization"""
    __tablename__ = "kb_categories"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    
    # Category details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Hierarchy
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("kb_categories.id"), nullable=True, index=True
    )
    
    # Visibility
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    
    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="kb_categories")
    articles: Mapped[List["KBArticle"]] = relationship("KBArticle", back_populates="category")
    parent: Mapped[Optional["KBCategory"]] = relationship("KBCategory", remote_side=[id], back_populates="children")
    children: Mapped[List["KBCategory"]] = relationship("KBCategory", back_populates="parent")
    
    def __repr__(self) -> str:
        return f"<KBCategory {self.name}>"
