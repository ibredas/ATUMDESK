#!/usr/bin/env python3
"""
Create or update admin user for ATUM DESK
"""
import asyncio
import sys
import argparse
from uuid import uuid4

sys.path.insert(0, '.')

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import hashlib
import secrets


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/atum_desk"


def hash_password(password: str) -> str:
    """Hash password using PBKDF2 (same as app auth)"""
    salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${key.hex()}"


async def create_admin_user(email: str, password: str, role: str = "ADMIN"):
    """Create or update admin user"""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get or create default organization
        org_result = await session.execute(
            text("SELECT id, name FROM organizations LIMIT 1")
        )
        org = org_result.fetchone()
        
        if not org:
            # Create default org
            org_id = uuid4()
            await session.execute(
                text("INSERT INTO organizations (id, name, created_at) VALUES (:id, :name, now())"),
                {"id": org_id, "name": "Default Organization"}
            )
            await session.commit()
            org = (org_id, "Default Organization")
            print(f"Created organization: {org[1]}")
        else:
            org_id = org[0]
            print(f"Using existing organization: {org[1]}")
        
        # Check if user exists
        user_result = await session.execute(
            text("SELECT id, email, role FROM users WHERE email ILIKE :email"),
            {"email": email}
        )
        user = user_result.fetchone()
        
        password_hash = hash_password(password)
        
        if user:
            # Update existing user
            user_id = user[0]
            await session.execute(
                text("""
                    UPDATE users 
                    SET password_hash = :password_hash, 
                        role = :role,
                        is_active = true,
                        updated_at = now()
                    WHERE id = :id
                """),
                {"id": user_id, "password_hash": password_hash, "role": role}
            )
            print(f"Updated user: {email} -> role={role}")
        else:
            # Create new user
            user_id = uuid4()
            await session.execute(
                text("""
                    INSERT INTO users (id, email, password_hash, full_name, role, organization_id, is_active, email_verified, two_factor_enabled, created_at, updated_at)
                    VALUES (:id, :email, :password_hash, :full_name, :role, :org_id, true, false, false, now(), now())
                """),
                {"id": user_id, "email": email, "password_hash": password_hash, "full_name": email.split('@')[0], "role": role, "org_id": org_id}
            )
            print(f"Created user: {email} -> role={role}")
        
        await session.commit()
        
        # Verify
        verify_result = await session.execute(
            text("SELECT id, email, role, is_active, created_at FROM users WHERE email ILIKE :email"),
            {"email": email}
        )
        user_row = verify_result.fetchone()
        print(f"\nVerification:")
        print(f"  ID: {user_row[0]}")
        print(f"  Email: {user_row[1]}")
        print(f"  Role: {user_row[2]}")
        print(f"  Active: {user_row[3]}")
        print(f"  Created: {user_row[4]}")
    
    await engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--email", default="ibreda@local", help="User email")
    parser.add_argument("--password", default="Mido@Meiam", help="User password")
    parser.add_argument("--role", default="ADMIN", help="User role")
    
    args = parser.parse_args()
    
    asyncio.run(create_admin_user(args.email, args.password, args.role))
