import csv
import io
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.db.session import get_session
from app.auth.deps import get_current_user
from app.models.user import User, UserRole
from app.models.ticket import Ticket

router = APIRouter()

@router.get("/tickets/export", response_class=Response)
async def export_tickets_csv(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Export tickets to CSV.
    Only Admins or Agents can export.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.AGENT]:
         raise HTTPException(status_code=403, detail="Not authorized to export data")

    # Fetch all tickets for the organization
    query = select(Ticket).where(
        Ticket.organization_id == current_user.organization_id
    ).order_by(desc(Ticket.created_at))
    
    result = await db.execute(query)
    tickets = result.scalars().all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Ticket ID", "Subject", "Status", "Priority", "Requester", 
        "Created At", "Resolved At", "SLA Breached?"
    ])
    
    for t in tickets:
        # Check SLA breach (simple check if calculation exists and is breached)
        # For MVP, we might need to join SLACalculation, but for now we skip complex joins
        # or we can lazily load if performance isn't an issue (it is for export)
        # Let's keep it simple for now.
        
        writer.writerow([
            str(t.id),
            t.subject,
            t.status.value,
            t.priority.value,
            str(t.requester_id),
            t.created_at.isoformat(),
            t.resolved_at.isoformat() if t.resolved_at else "",
            "N/A" # TODO: Join with SLACalculation for accuracy
        ])
    
    output.seek(0)
    
    filename = f"atum_tickets_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
