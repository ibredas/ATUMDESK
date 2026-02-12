import asyncio
import logging
import sys
import uuid
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.db.base import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.auth.jwt import get_password_hash
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_admin():
    async with AsyncSessionLocal() as session:
        # 1. Get or Create Organization
        org_name = "ATUM"
        result = await session.execute(select(Organization).where(Organization.name == org_name))
        org = result.scalar_one_or_none()
        
        if not org:
            logger.info(f"Creating organization {org_name}...")
            org = Organization(
                name=org_name,
                slug="atum",
                is_active=True
            )
            session.add(org)
            await session.flush() # Get ID
        else:
            logger.info(f"Using existing organization {org.name}")

        # 2. Create Admin User
        email = "admin@atum.io"
        password = "admin"
        
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info(f"User {email} already exists")
            return

        logger.info(f"Creating admin user {email}...")
        
        db_user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name="System Admin",
            role=UserRole.ADMIN,
            is_active=True,
            email_verified=True,
            organization_id=org.id
        )
        
        session.add(db_user)
        try:
            await session.commit()
            logger.info("Admin user created successfully")
        except Exception as e:
            logger.error(f"Failed to create admin: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(create_admin())
