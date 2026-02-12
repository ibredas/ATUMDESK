"""
Domain Repository Interfaces (Abstract)
Following Repository Pattern & Dependency Inversion Principle
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities import (
    Organization, OrganizationId,
    User, UserId,
    Ticket, TicketId,
    SLAPolicy,
    KBArticle,
    CannedResponse,
)


class RepositoryError(Exception):
    """Base exception for repository errors"""
    pass


class EntityNotFoundError(RepositoryError):
    """Raised when entity is not found"""
    pass


class DuplicateEntityError(RepositoryError):
    """Raised when duplicate entity exists"""
    pass


class IOrganizationRepository(ABC):
    """Abstract repository for Organization aggregate"""
    
    @abstractmethod
    async def get_by_id(self, org_id: OrganizationId) -> Optional[Organization]:
        """Get organization by ID"""
        pass
    
    @abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Organization]:
        """Get organization by slug"""
        pass
    
    @abstractmethod
    async def create(self, organization: Organization) -> Organization:
        """Create new organization"""
        pass
    
    @abstractmethod
    async def update(self, organization: Organization) -> Organization:
        """Update organization"""
        pass
    
    @abstractmethod
    async def delete(self, org_id: OrganizationId) -> bool:
        """Soft delete organization"""
        pass
    
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> List[Organization]:
        """List all organizations"""
        pass


class IUserRepository(ABC):
    """Abstract repository for User aggregate"""
    
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_by_org_and_email(self, org_id: OrganizationId, email: str) -> Optional[User]:
        """Get user by organization and email (multi-tenant)"""
        pass
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create new user"""
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Soft delete user"""
        pass
    
    @abstractmethod
    async def list_by_organization(
        self, 
        org_id: OrganizationId, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[User]:
        """List users in organization"""
        pass


class ITicketRepository(ABC):
    """Abstract repository for Ticket aggregate"""
    
    @abstractmethod
    async def get_by_id(self, ticket_id: TicketId) -> Optional[Ticket]:
        """Get ticket by ID"""
        pass
    
    @abstractmethod
    async def create(self, ticket: Ticket) -> Ticket:
        """Create new ticket"""
        pass
    
    @abstractmethod
    async def update(self, ticket: Ticket) -> Ticket:
        """Update ticket"""
        pass
    
    @abstractmethod
    async def delete(self, ticket_id: TicketId) -> bool:
        """Delete ticket"""
        pass
    
    @abstractmethod
    async def list_by_organization(
        self,
        org_id: OrganizationId,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets in organization"""
        pass
    
    @abstractmethod
    async def list_by_requester(
        self,
        requester_id: UserId,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets by requester"""
        pass
    
    @abstractmethod
    async def list_by_assignee(
        self,
        assignee_id: UserId,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets assigned to user"""
        pass
    
    @abstractmethod
    async def list_by_status(
        self,
        org_id: OrganizationId,
        status: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """List tickets by status"""
        pass
    
    @abstractmethod
    async def search(
        self,
        org_id: OrganizationId,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Ticket]:
        """Search tickets"""
        pass


class ISLARepository(ABC):
    """Abstract repository for SLA Policy"""
    
    @abstractmethod
    async def get_by_id(self, policy_id: UUID) -> Optional[SLAPolicy]:
        """Get SLA policy by ID"""
        pass
    
    @abstractmethod
    async def get_default_for_organization(self, org_id: OrganizationId) -> Optional[SLAPolicy]:
        """Get default SLA policy for organization"""
        pass
    
    @abstractmethod
    async def create(self, policy: SLAPolicy) -> SLAPolicy:
        """Create SLA policy"""
        pass
    
    @abstractmethod
    async def update(self, policy: SLAPolicy) -> SLAPolicy:
        """Update SLA policy"""
        pass


class IKBRepository(ABC):
    """Abstract repository for Knowledge Base"""
    
    @abstractmethod
    async def get_article_by_id(self, article_id: UUID) -> Optional[KBArticle]:
        """Get article by ID"""
        pass
    
    @abstractmethod
    async def get_article_by_slug(self, slug: str) -> Optional[KBArticle]:
        """Get article by slug"""
        pass
    
    @abstractmethod
    async def create_article(self, article: KBArticle) -> KBArticle:
        """Create article"""
        pass
    
    @abstractmethod
    async def update_article(self, article: KBArticle) -> KBArticle:
        """Update article"""
        pass
    
    @abstractmethod
    async def search_articles(
        self,
        org_id: OrganizationId,
        query: str,
        include_internal: bool = False,
    ) -> List[KBArticle]:
        """Search articles"""
        pass


class ICannedResponseRepository(ABC):
    """Abstract repository for Canned Responses"""
    
    @abstractmethod
    async def get_by_id(self, response_id: UUID) -> Optional[CannedResponse]:
        """Get canned response by ID"""
        pass
    
    @abstractmethod
    async def list_by_organization(
        self,
        org_id: OrganizationId,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CannedResponse]:
        """List canned responses"""
        pass
    
    @abstractmethod
    async def create(self, response: CannedResponse) -> CannedResponse:
        """Create canned response"""
        pass
    
    @abstractmethod
    async def update(self, response: CannedResponse) -> CannedResponse:
        """Update canned response"""
        pass
    
    @abstractmethod
    async def delete(self, response_id: UUID) -> bool:
        """Delete canned response"""
        pass
