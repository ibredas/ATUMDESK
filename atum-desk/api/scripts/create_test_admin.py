import asyncio
import logging
import sys
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

async def create_test_admin():
    async with AsyncSessionLocal() as session:
        # 1. Get Organization
        org_name = "ATUM"
        result = await session.execute(select(Organization).where(Organization.name == org_name))
        org = result.scalar_one_or_none()
        
        if not org:
            logger.info(f"Creating organization {org_name}...")
            org = Organization(name=org_name, slug="atum", is_active=True)
            session.add(org)
            await session.flush()
        
        # 2. Create Test Admin
        email = "admin_test@atum.io"
        password = "password123"
        
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info(f"Test Admin {email} already exists. Updating password...")
            existing.password_hash = get_password_hash(password)
            existing.role = UserRole.ADMIN # Ensure role
        else:
            logger.info(f"Creating Test Admin {email}...")
            db_user = User(
                email=email,
                password_hash=get_password_hash(password),
                full_name="Test Admin",
                role=UserRole.ADMIN,
                is_active=True,
                email_verified=True,
                organization_id=org.id
            )
            session.add(db_user)
            
        await session.commit()
        logger.info(f"Test Admin {email} ready with password: {password}")

if __name__ == "__main__":
    asyncio.run(create_test_admin())
