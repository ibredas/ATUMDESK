"""
Ticket Controller - Interface Adapter Layer
Converts HTTP requests to use case calls and vice versa
"""
from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status

from src.domain.entities import (
    TicketId, TicketStatus,
    UserId, OrganizationId,
    Priority,
)
from src.usecases.ticket import (
    CreateTicketRequest, CreateTicketResponse,
    AcceptTicketRequest,
    AssignTicketRequest,
    ChangeStatusRequest,
)
from src.frameworks.config.container import get_container


class TicketController:
    """
    Controller: Ticket Operations
    Handles HTTP request/response conversion
    """
    
    async def create_ticket(
        self,
        organization_id: UUID,
        requester_id: UUID,
        service_id: UUID,
        subject: str,
        description: str,
        priority: str = "medium",
    ) -> dict:
        """
        Controller method: Create ticket
        Converts HTTP params to use case request
        """
        container = get_container()
        
        # Convert to domain types
        try:
            priority_enum = Priority(priority)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid priority: {priority}"
            )
        
        use_case_request = CreateTicketRequest(
            organization_id=OrganizationId(organization_id),
            requester_id=UserId(requester_id),
            service_id=service_id,
            subject=subject,
            description=description,
            priority=priority_enum,
        )
        
        # Execute use case
        async with container.get_create_ticket_use_case() as use_case:
            result = await use_case.execute(use_case_request)
        
        # Convert to response
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.message
            )
        
        return self._ticket_to_dict(result.ticket)
    
    async def accept_ticket(
        self,
        ticket_id: UUID,
        manager_id: UUID,
    ) -> dict:
        """Controller method: Accept ticket"""
        container = get_container()
        
        use_case_request = AcceptTicketRequest(
            ticket_id=TicketId(ticket_id),
            manager_id=UserId(manager_id),
        )
        
        try:
            async with container.get_accept_ticket_use_case() as use_case:
                ticket = await use_case.execute(use_case_request)
        except PermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        return self._ticket_to_dict(ticket)
    
    async def assign_ticket(
        self,
        ticket_id: UUID,
        agent_id: UUID,
        assigned_by: UUID,
    ) -> dict:
        """Controller method: Assign ticket"""
        container = get_container()
        
        use_case_request = AssignTicketRequest(
            ticket_id=TicketId(ticket_id),
            agent_id=UserId(agent_id),
            assigned_by=UserId(assigned_by),
        )
        
        try:
            async with container.get_assign_ticket_use_case() as use_case:
                ticket = await use_case.execute(use_case_request)
        except PermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        return self._ticket_to_dict(ticket)
    
    async def change_status(
        self,
        ticket_id: UUID,
        new_status: str,
        user_id: UUID,
        comment: Optional[str] = None,
    ) -> dict:
        """Controller method: Change ticket status"""
        container = get_container()
        
        # Convert status
        try:
            status_enum = TicketStatus(new_status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {new_status}"
            )
        
        use_case_request = ChangeStatusRequest(
            ticket_id=TicketId(ticket_id),
            new_status=status_enum,
            user_id=UserId(user_id),
            comment=comment,
        )
        
        try:
            async with container.get_change_status_use_case() as use_case:
                ticket = await use_case.execute(use_case_request)
        except PermissionError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        
        return self._ticket_to_dict(ticket)
    
    async def list_tickets(
        self,
        organization_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        requester_id: Optional[UUID] = None,
        assignee_id: Optional[UUID] = None,
    ) -> list:
        """Controller method: List tickets with filters"""
        container = get_container()
        
        async with container.get_ticket_repository() as repo:
            if status:
                tickets = await repo.list_by_status(
                    OrganizationId(organization_id),
                    status,
                    skip,
                    limit,
                )
            elif requester_id:
                tickets = await repo.list_by_requester(
                    UserId(requester_id),
                    skip,
                    limit,
                )
            elif assignee_id:
                tickets = await repo.list_by_assignee(
                    UserId(assignee_id),
                    skip,
                    limit,
                )
            else:
                tickets = await repo.list_by_organization(
                    OrganizationId(organization_id),
                    skip,
                    limit,
                )
        
        return [self._ticket_to_dict(t) for t in tickets]
    
    def _ticket_to_dict(self, ticket) -> dict:
        """Convert domain entity to API response dict"""
        return {
            "id": str(ticket.id),
            "organization_id": str(ticket.organization_id),
            "requester_id": str(ticket.requester_id),
            "service_id": str(ticket.service_id),
            "subject": ticket.subject,
            "description": ticket.description,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "assigned_to": str(ticket.assigned_to) if ticket.assigned_to else None,
            "accepted_by": str(ticket.accepted_by) if ticket.accepted_by else None,
            "accepted_at": ticket.accepted_at.isoformat() if ticket.accepted_at else None,
            "sla_due_at": ticket.sla_due_at.isoformat() if ticket.sla_due_at else None,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
            "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else None,
            "closed_at": ticket.closed_at.isoformat() if ticket.closed_at else None,
        }


# Singleton controller instance
ticket_controller = TicketController()
