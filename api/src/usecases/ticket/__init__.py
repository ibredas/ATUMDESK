"""
Ticket Use Cases - Application Business Rules
Following Clean Architecture: Use Cases orchestrate domain entities
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.entities import (
    Ticket, TicketId, TicketStatus,
    User, UserId, UserRole,
    OrganizationId,
    Comment,
    SLAPolicy,
    Priority,
)
from src.domain.repositories import (
    ITicketRepository,
    IUserRepository,
    ISLARepository,
    EntityNotFoundError,
)


@dataclass
class CreateTicketRequest:
    """DTO: Request to create ticket"""
    organization_id: OrganizationId
    requester_id: UserId
    service_id: UUID
    subject: str
    description: str
    priority: Priority = Priority.MEDIUM


@dataclass
class CreateTicketResponse:
    """DTO: Response from create ticket"""
    ticket: Ticket
    success: bool
    message: str = ""


@dataclass
class AcceptTicketRequest:
    """DTO: Request to accept ticket"""
    ticket_id: TicketId
    manager_id: UserId


@dataclass
class AssignTicketRequest:
    """DTO: Request to assign ticket"""
    ticket_id: TicketId
    agent_id: UserId
    assigned_by: UserId


@dataclass
class ChangeStatusRequest:
    """DTO: Request to change ticket status"""
    ticket_id: TicketId
    new_status: TicketStatus
    user_id: UserId
    comment: Optional[str] = None


class CreateTicketUseCase:
    """
    Use Case: Create a new ticket
    
    Business Rules:
    - Requester must be active
    - Subject and description required
    - Ticket starts in NEW status
    - SLA policy applied based on organization
    """
    
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        user_repo: IUserRepository,
        sla_repo: ISLARepository,
    ):
        self.ticket_repo = ticket_repo
        self.user_repo = user_repo
        self.sla_repo = sla_repo
    
    async def execute(self, request: CreateTicketRequest) -> CreateTicketResponse:
        """Execute create ticket use case"""
        # Validate requester exists
        requester = await self.user_repo.get_by_id(request.requester_id)
        if not requester:
            return CreateTicketResponse(
                ticket=None,
                success=False,
                message="Requester not found"
            )
        
        if not requester.is_active:
            return CreateTicketResponse(
                ticket=None,
                success=False,
                message="Requester account is inactive"
            )
        
        # Validate requester belongs to organization
        if requester.organization_id != request.organization_id:
            return CreateTicketResponse(
                ticket=None,
                success=False,
                message="Requester does not belong to organization"
            )
        
        # Create ticket
        ticket = Ticket(
            id=TicketId.generate(),
            organization_id=request.organization_id,
            requester_id=request.requester_id,
            service_id=request.service_id,
            subject=request.subject,
            description=request.description,
            priority=request.priority,
            status=TicketStatus.NEW,
        )
        
        # Apply SLA policy
        sla_policy = await self.sla_repo.get_default_for_organization(
            request.organization_id
        )
        if sla_policy:
            ticket.sla_due_at = ticket.calculate_sla_deadline(
                sla_policy.get_response_time(request.priority)
            )
        
        # Save ticket
        created_ticket = await self.ticket_repo.create(ticket)
        
        return CreateTicketResponse(
            ticket=created_ticket,
            success=True,
            message="Ticket created successfully"
        )


class AcceptTicketUseCase:
    """
    Use Case: Manager accepts a ticket
    
    Business Rules:
    - Only managers or admins can accept
    - Ticket must be in NEW status
    - Sets accepted_by and accepted_at
    - Starts SLA timer
    """
    
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        user_repo: IUserRepository,
    ):
        self.ticket_repo = ticket_repo
        self.user_repo = user_repo
    
    async def execute(self, request: AcceptTicketRequest) -> Ticket:
        """Execute accept ticket use case"""
        # Get manager
        manager = await self.user_repo.get_by_id(request.manager_id)
        if not manager:
            raise EntityNotFoundError("Manager not found")
        
        # Check permission
        if not manager.has_permission(UserRole.MANAGER):
            raise PermissionError("Only managers can accept tickets")
        
        # Get ticket
        ticket = await self.ticket_repo.get_by_id(request.ticket_id)
        if not ticket:
            raise EntityNotFoundError("Ticket not found")
        
        # Check manager's organization matches ticket
        if ticket.organization_id != manager.organization_id:
            raise PermissionError("Cannot accept tickets from other organizations")
        
        # Execute domain logic
        ticket.accept(request.manager_id)
        
        # Save
        return await self.ticket_repo.update(ticket)


class AssignTicketUseCase:
    """
    Use Case: Assign ticket to agent
    
    Business Rules:
    - Only managers can assign
    - Ticket must be ACCEPTED or NEW
    - Agent must be in same organization
    - Agent must have AGENT role or higher
    """
    
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        user_repo: IUserRepository,
    ):
        self.ticket_repo = ticket_repo
        self.user_repo = user_repo
    
    async def execute(self, request: AssignTicketRequest) -> Ticket:
        """Execute assign ticket use case"""
        # Get assigner
        assigner = await self.user_repo.get_by_id(request.assigned_by)
        if not assigner:
            raise EntityNotFoundError("Assigner not found")
        
        if not assigner.has_permission(UserRole.MANAGER):
            raise PermissionError("Only managers can assign tickets")
        
        # Get agent
        agent = await self.user_repo.get_by_id(request.agent_id)
        if not agent:
            raise EntityNotFoundError("Agent not found")
        
        if not agent.has_permission(UserRole.AGENT):
            raise PermissionError("User must be an agent or higher")
        
        # Get ticket
        ticket = await self.ticket_repo.get_by_id(request.ticket_id)
        if not ticket:
            raise EntityNotFoundError("Ticket not found")
        
        # Check organization match
        if ticket.organization_id != assigner.organization_id:
            raise PermissionError("Ticket does not belong to your organization")
        
        if agent.organization_id != ticket.organization_id:
            raise PermissionError("Agent does not belong to ticket organization")
        
        # Execute domain logic
        ticket.assign(request.agent_id)
        
        return await self.ticket_repo.update(ticket)


class ChangeTicketStatusUseCase:
    """
    Use Case: Change ticket status
    
    Business Rules:
    - Validates status transitions
    - Handles SLA pause/resume
    - Records comment if provided
    """
    
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        user_repo: IUserRepository,
    ):
        self.ticket_repo = ticket_repo
        self.user_repo = user_repo
    
    async def execute(self, request: ChangeStatusRequest) -> Ticket:
        """Execute change status use case"""
        # Get user
        user = await self.user_repo.get_by_id(request.user_id)
        if not user:
            raise EntityNotFoundError("User not found")
        
        # Get ticket
        ticket = await self.ticket_repo.get_by_id(request.ticket_id)
        if not ticket:
            raise EntityNotFoundError("Ticket not found")
        
        # Check organization
        if ticket.organization_id != user.organization_id:
            raise PermissionError("Cannot modify tickets from other organizations")
        
        # Check permission based on status change
        if request.new_status in [TicketStatus.ACCEPTED, TicketStatus.ASSIGNED]:
            if not user.has_permission(UserRole.MANAGER):
                raise PermissionError("Only managers can perform this action")
        
        # Execute domain logic
        ticket.change_status(request.new_status, user)
        
        # Add comment if provided
        if request.comment:
            comment = Comment(
                author_id=request.user_id,
                content=request.comment,
                is_internal=False,
            )
            ticket.add_comment(comment)
        
        return await self.ticket_repo.update(ticket)


class AddCommentUseCase:
    """
    Use Case: Add comment to ticket
    
    Business Rules:
    - User must have access to ticket
    - Internal comments only by agents+
    """
    
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        user_repo: IUserRepository,
    ):
        self.ticket_repo = ticket_repo
        self.user_repo = user_repo
    
    async def execute(
        self,
        ticket_id: TicketId,
        author_id: UserId,
        content: str,
        is_internal: bool = False,
    ) -> Ticket:
        """Execute add comment use case"""
        # Get user
        author = await self.user_repo.get_by_id(author_id)
        if not author:
            raise EntityNotFoundError("Author not found")
        
        # Get ticket
        ticket = await self.ticket_repo.get_by_id(ticket_id)
        if not ticket:
            raise EntityNotFoundError("Ticket not found")
        
        # Check access
        if not author.can_view_ticket(ticket.organization_id):
            raise PermissionError("Cannot access this ticket")
        
        # Check internal comment permission
        if is_internal and not author.has_permission(UserRole.AGENT):
            raise PermissionError("Only agents can add internal comments")
        
        # Create and add comment
        comment = Comment(
            author_id=author_id,
            content=content,
            is_internal=is_internal,
        )
        ticket.add_comment(comment)
        
        return await self.ticket_repo.update(ticket)
