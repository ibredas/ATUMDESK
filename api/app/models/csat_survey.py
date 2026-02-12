"""
ATUM DESK - CSAT Survey Model
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class CSATSurvey(Base):
    """Customer satisfaction surveys"""
    __tablename__ = "csat_surveys"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tickets.id"), nullable=False, index=True
    )
    
    # Rating (1-5 stars)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Respondent info
    respondent_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Type
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)  # Internal agent rating
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    
    # Relationships
    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="csat_surveys")
    
    def __repr__(self) -> str:
        return f"<CSATSurvey ticket={self.ticket_id} rating={self.rating}>"
    
    @property
    def rating_label(self) -> str:
        """Get label for rating"""
        labels = {
            1: "Very Dissatisfied",
            2: "Dissatisfied",
            3: "Neutral",
            4: "Satisfied",
            5: "Very Satisfied"
        }
        return labels.get(self.rating, "Unknown")
