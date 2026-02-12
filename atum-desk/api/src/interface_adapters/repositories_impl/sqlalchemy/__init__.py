"""
SQLAlchemy Repository Implementations
Infrastructure layer - implements domain repository interfaces
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.domain.entities import (
    Ticket, TicketId, TicketStatus,
    User, UserId, UserRole,
    Organization, OrganizationId,
    Email,
)
from src.domain.repositories import (
    ITicketRepository,
    IUserRepository,
    IOrganizationRepository,
    EntityNotFoundError,
)


class SQLAlchemyTicketRepository(ITicketRepository):
    """
    SQLAlchemy implementation of Ticket Repository
    Implements Unit of Work pattern via session
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, ticket_id: TicketId) -> Optional[Ticket]:
        """Get ticket by ID with all related data"""
        from app.models.ticket import TicketModel
        
        result = await self.session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id.value)
        )
        db_ticket = result.scalar_one_or_none()
        
        if not db_ticket:
            return None
        
        return self._to_domain_entity(db_ticket)
    
    async def create(self, ticket: Ticket) -> Ticket:
        """Create new ticket"""
        from app.models.ticket import TicketModel
        
        db_ticket = TicketModel(
            id=ticket.id.value,
            organization_id=ticket.organization_id.value,
            requester_id=ticket.requester_id.value,
            service_id=ticket.service_id,
            subject=ticket.subject,
            description=ticket.description,
            status=ticket.status.value,
            priority=ticket.priority.value,
            assigned_to=ticket.assigned_to.value if ticket.assigned_to else None,
            accepted_by=ticket.accepted_by.value if ticket.accepted_by else None,
            accepted_at=ticket.accepted_at,
            sla_due_at=ticket.sla_due_at,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )
        
        self.session.add(db_ticket)
        await self.session.flush()
        
        return ticket
    
    async def update(self, ticket: Ticket) -> Ticket:
        """Update existing ticket"""
        from app.models.ticket import TicketModel
        
        result = await self.session.execute(
            select(TicketModel).where(TicketModel.id == ticket.id.value)
        )
        db_ticket = result.scalar_one_or_none()
        
        if not db_ticket:
            raise EntityNotFoundError(f"Ticket {ticket.id} not found")
        
        # Update fields
        db_ticket.subject = ticket.subject
        db_ticket.description = ticket.description
        db_ticket.status = ticket.status.value
        db_ticket.priority = ticket.priority.value
        db_ticket.assigned_to = ticket.assigned_to.value if ticket.assigned_to else None
        db_ticket.accepted_by = ticket.accepted_by.value if ticket.accepted_by else None
        db_ticket.accepted_at = ticket.accepted_at
        db_ticket.sla_due_at = ticket.sla_due_at
        db_ticket.sla_paused_at = ticket.sla_paused_at
        db_ticket.sla_paused_duration = ticket.sla_paused_duration
        db_ticket.resolved_at = ticket.resolved_at
        db_ticket.closed_at = ticket.closed_at
        db_ticket.updated_at = ticket.updated_at
        
        await self.session.flush()
        
        return ticket
    
    async def delete(self, ticket_id: TicketId) -> bool:
        """Soft delete ticket"""
        from app.models.ticket import TicketModel
        
        result = await self.session.execute(
            select(TicketModel).where(TicketModel.id == ticket_id.value)
        )
        db_ticket = result.scalar_one_or_none()
        
        if not db_ticket:
            return False
        
        db_ticket.is_deleted = True
        await self.session.flush()
        
        return True
    
    async def list_by_organization(
        self,
        org_id: OrganizationId,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets in organization"""
        from app.models.ticket import TicketModel
        
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.organization_id == org_id.value)
            .where(TicketModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(TicketModel.created_at.desc())
        )
        
        db_tickets = result.scalars().all()
        return [self._to_domain_entity(t) for t in db_tickets]
    
    async def list_by_requester(
        self,
        requester_id: UserId,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets by requester"""
        from app.models.ticket import TicketModel
        
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.requester_id == requester_id.value)
            .where(TicketModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(TicketModel.created_at.desc())
        )
        
        db_tickets = result.scalars().all()
        return [self._to_domain_entity(t) for t in db_tickets]
    
    async def list_by_assignee(
        self,
        assignee_id: UserId,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets assigned to user"""
        from app.models.ticket import TicketModel
        
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.assigned_to == assignee_id.value)
            .where(TicketModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(TicketModel.created_at.desc())
        )
        
        db_tickets = result.scalars().all()
        return [self._to_domain_entity(t) for t in db_tickets]
    
    async def list_by_status(
        self,
        org_id: OrganizationId,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets by status"""
        from app.models.ticket import TicketModel
        
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.organization_id == org_id.value)
            .where(TicketModel.status == status)
            .where(TicketModel.is_deleted == False)
            .offset(skip)
            .limit(limit)
            .order_by(TicketModel.created_at.desc())
        )
        
        db_tickets = result.scalars().all()
        return [self._to_domain_entity(t) for t in db_tickets]
    
    async def search(
        self,
        org_id: OrganizationId,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """Search tickets using full-text search"""
        from app.models.ticket import TicketModel
        from sqlalchemy import or_, func
        
        result = await self.session.execute(
            select(TicketModel)
            .where(TicketModel.organization_id == org_id.value)
            .where(TicketModel.is_deleted == False)
            .where(
                or_(
                    TicketModel.subject.ilike(f"%{query}%"),
                    TicketModel.description.ilike(f"%{query}%"),
                )
            )
            .offset(skip)
            .limit(limit)
            .order_by(TicketModel.created_at.desc())
        )
        
        db_tickets = result.scalars().all()
        return [self._to_domain_entity(t) for t in db_tickets]
    
    def _to_domain_entity(self, db_ticket) -> Ticket:
        """Map database model to domain entity"""
        return Ticket(
            id=TicketId(db_ticket.id),
            organization_id=OrganizationId(db_ticket.organization_id),
            requester_id=UserId(db_ticket.requester_id),
            service_id=db_ticket.service_id,
            subject=db_ticket.subject,
            description=db_ticket.description,
            status=TicketStatus(db_ticket.status),
            priority=Priority(db_ticket.priority),
            assigned_to=UserId(db_ticket.assigned_to) if db_ticket.assigned_to else None,
            accepted_by=UserId(db_ticket.accepted_by) if db_ticket.accepted_by else None,
            accepted_at=db_ticket.accepted_at,
            sla_due_at=db_ticket.sla_due_at,
            sla_paused_at=db_ticket.sla_paused_at,
            sla_paused_duration=db_ticket.sla_paused_duration,
            created_at=db_ticket.created_at,
            updated_at=db_ticket.updated_at,
            resolved_at=db_ticket.resolved_at,
            closed_at=db_ticket.closed_at,
        )


class SQLAlchemyUserRepository(IUserRepository):
    """
    SQLAlchemy implementation of User Repository
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID"""
        from app.models.user import UserModel
        
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id.value)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return self._to_domain_entity(db_user)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        from app.models.user import UserModel
        
        result = await self.session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return self._to_domain_entity(db_user)
    
    async def get_by_org_and_email(
        self, 
        org_id: OrganizationId, 
        email: str
    ) -> Optional[User]:
        """Get user by organization and email (multi-tenant)"""
        from app.models.user import UserModel
        
        result = await self.session.execute(
            select(UserModel).where(
                and_(
                    UserModel.organization_id == org_id.value,
                    UserModel.email == email,
                )
            )
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return None
        
        return self._to_domain_entity(db_user)
    
    async def create(self, user: User) -> User:
        """Create new user"""
        from app.models.user import UserModel
        
        db_user = UserModel(
            id=user.id.value,
            organization_id=user.organization_id.value,
            email=user.email.value,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            email_verified=user.email_verified,
            two_factor_enabled=user.two_factor_enabled,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        
        self.session.add(db_user)
        await self.session.flush()
        
        return user
    
    async def update(self, user: User) -> User:
        """Update user"""
        from app.models.user import UserModel
        
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user.id.value)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            raise EntityNotFoundError(f"User {user.id} not found")
        
        db_user.full_name = user.full_name
        db_user.role = user.role.value
        db_user.is_active = user.is_active
        db_user.email_verified = user.email_verified
        db_user.two_factor_enabled = user.two_factor_enabled
        db_user.updated_at = user.updated_at
        
        await self.session.flush()
        
        return user
    
    async def delete(self, user_id: UserId) -> bool:
        """Soft delete user"""
        from app.models.user import UserModel
        
        result = await self.session.execute(
            select(UserModel).where(UserModel.id == user_id.value)
        )
        db_user = result.scalar_one_or_none()
        
        if not db_user:
            return False
        
        db_user.is_active = False
        db_user.updated_at = datetime.utcnow()
        await self.session.flush()
        
        return True
    
    async def list_by_organization(
        self, 
        org_id: OrganizationId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """List users in organization"""
        from app.models.user import UserModel
        
        result = await self.session.execute(
            select(UserModel)
            .where(UserModel.organization_id == org_id.value)
            .offset(skip)
            .limit(limit)
            .order_by(UserModel.created_at.desc())
        )
        
        db_users = result.scalars().all()
        return [self._to_domain_entity(u) for u in db_users]
    
    def _to_domain_entity(self, db_user) -> User:
        """Map database model to domain entity"""
        return User(
            id=UserId(db_user.id),
            organization_id=OrganizationId(db_user.organization_id),
            email=Email(db_user.email),
            full_name=db_user.full_name,
            role=UserRole(db_user.role),
            is_active=db_user.is_active,
            email_verified=db_user.email_verified,
            two_factor_enabled=db_user.two_factor_enabled,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        )
