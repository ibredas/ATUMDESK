import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, or_, and_
from pydantic import BaseModel

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.asset import Asset, TicketAssetLink
from app.models.ticket import Ticket

router = APIRouter()

# --- Pydantic Models ---
class AssetCreate(BaseModel):
    name: str
    identifier: str
    asset_type: str
    assigned_user_id: Optional[uuid.UUID] = None
    metadata_json: Optional[Dict[str, Any]] = {}

class AssetUpdate(BaseModel):
    name: Optional[str] = None
    identifier: Optional[str] = None
    asset_type: Optional[str] = None
    assigned_user_id: Optional[uuid.UUID] = None
    metadata_json: Optional[Dict[str, Any]] = None

class AssetResponse(BaseModel):
    id: uuid.UUID
    name: str
    identifier: str
    asset_type: str
    assigned_user_id: Optional[uuid.UUID]
    metadata_json: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

# --- Routes ---

@router.get("", response_model=List[AssetResponse])
async def list_assets(
    search: Optional[str] = None,
    asset_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """List Assets (Agent Only)"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    query = select(Asset).where(Asset.organization_id == current_user.organization_id)
    
    if asset_type:
        query = query.where(Asset.asset_type == asset_type)
        
    if search:
        term = f"%{search}%"
        query = query.where(or_(
            Asset.name.ilike(term),
            Asset.identifier.ilike(term)
        ))
        
    result = await db.execute(query.order_by(desc(Asset.updated_at)))
    return result.scalars().all()

@router.post("", response_model=AssetResponse)
async def create_asset(
    data: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Create Asset"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    # Check Identifier Uniqueness
    existing = await db.execute(select(Asset).where(
        Asset.organization_id == current_user.organization_id,
        Asset.identifier == data.identifier
    ))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Asset Identifier already exists")
        
    asset = Asset(
        organization_id=current_user.organization_id,
        name=data.name,
        identifier=data.identifier,
        asset_type=data.asset_type,
        assigned_user_id=data.assigned_user_id,
        metadata_json=data.metadata_json or {},
        created_by=current_user.id
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset

@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Get Asset Detail"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Asset).where(
        Asset.id == asset_id, 
        Asset.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
        
    return asset

@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: uuid.UUID,
    data: AssetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Update Asset"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")

    query = select(Asset).where(
        Asset.id == asset_id, 
        Asset.organization_id == current_user.organization_id
    )
    result = await db.execute(query)
    asset = result.scalar_one_or_none()
    
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if data.name: asset.name = data.name
    if data.identifier: asset.identifier = data.identifier # Should check unique if changed
    if data.asset_type: asset.asset_type = data.asset_type
    if data.assigned_user_id is not None: asset.assigned_user_id = data.assigned_user_id
    if data.metadata_json: asset.metadata_json = data.metadata_json
    
    asset.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(asset)
    return asset

@router.post("/{asset_id}/link-ticket", status_code=201)
async def link_ticket(
    asset_id: uuid.UUID,
    ticket_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Link ticket to asset"""
    if current_user.role == UserRole.CUSTOMER_USER:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    asset_q = select(Asset).where(Asset.id == asset_id, Asset.organization_id == current_user.organization_id)
    if not (await db.execute(asset_q)).scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Asset not found")
         
    ticket_q = select(Ticket).where(Ticket.id == ticket_id, Ticket.organization_id == current_user.organization_id)
    if not (await db.execute(ticket_q)).scalar_one_or_none():
         raise HTTPException(status_code=404, detail="Ticket not found")
         
    link = TicketAssetLink(
        organization_id=current_user.organization_id,
        asset_id=asset_id,
        ticket_id=ticket_id,
        created_by=current_user.id
    )
    db.add(link)
    await db.commit()
    return {"status": "linked"}
