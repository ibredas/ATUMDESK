"""
ATUM DESK - Database Initialization
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base, engine
from app.models import (
    Organization, User, Service, Ticket, Comment, Attachment,
    SLAPolicy, SLACalculation, AuditLog, TimeEntry, TicketRelationship,
    CustomField, CustomFieldValue, CannedResponse, KBCategory, KBArticle, CSATSurvey
)

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def create_default_data(db: AsyncSession) -> None:
    """Create default data (admin org, default SLA policy, etc.)"""
    # This will be implemented with actual seed data
    pass
