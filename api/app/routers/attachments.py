"""
ATUM DESK - Attachments Router
"""
import os
import hashlib
import uuid
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from sqlalchemy import select

from app.db.session import get_session
from app.config import get_settings
from app.auth.jwt import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket
from app.models.attachment import Attachment

router = APIRouter()
settings = get_settings()


class AttachmentResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    created_at: datetime


@router.post("/ticket/{ticket_id}", response_model=AttachmentResponse)
async def upload_attachment(
    ticket_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Upload attachment to ticket"""
    from uuid import UUID as UUID_TYPE
    try:
        ticket_uuid = UUID_TYPE(ticket_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ticket ID")
    
    # Verify ticket access
    result = await db.execute(
        select(Ticket).where(
            Ticket.id == ticket_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Authorization
    if current_user.role == UserRole.CUSTOMER_USER:
        if ticket.requester_id != current_user.id:
            raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Validate extension
    file_ext = os.path.splitext(file.filename)[1][1:].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    # Generate safe filename
    file_id = uuid.uuid4()
    safe_filename = f"{file_id}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Calculate hash
    file_hash = hashlib.sha256(contents).hexdigest()
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Create database record
    attachment = Attachment(
        ticket_id=ticket_uuid,
        filename=safe_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(contents),
        mime_type=file.content_type or "application/octet-stream",
        file_hash=file_hash,
        uploaded_by=current_user.id
    )
    
    db.add(attachment)
    await db.flush()
    
    return AttachmentResponse(
        id=str(attachment.id),
        filename=attachment.filename,
        original_filename=attachment.original_filename,
        file_size=attachment.file_size,
        mime_type=attachment.mime_type,
        created_at=attachment.created_at
    )


@router.get("/{attachment_id}/download")
async def download_attachment(
    attachment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """Download attachment"""
    from uuid import UUID as UUID_TYPE
    try:
        attachment_uuid = UUID_TYPE(attachment_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid attachment ID")
    
    result = await db.execute(
        select(Attachment, Ticket).join(
            Ticket, Attachment.ticket_id == Ticket.id
        ).where(
            Attachment.id == attachment_uuid,
            Ticket.organization_id == current_user.organization_id
        )
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    attachment, ticket = row
    
    # Authorization
    if current_user.role == UserRole.CUSTOMER_USER:
        if ticket.requester_id != current_user.id:
            raise HTTPException(status_code=404, detail="Attachment not found")
    
    # Update access tracking
    attachment.access_count += 1
    attachment.last_accessed_at = datetime.utcnow()
    
    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.mime_type
    )
