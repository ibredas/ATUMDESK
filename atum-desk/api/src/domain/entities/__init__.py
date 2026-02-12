"""
ATUM DESK - Clean Architecture Domain Layer
Following Uncle Bob's Clean Architecture & DDD principles
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4


class TicketStatus(Enum):
    """Ticket lifecycle states"""
    NEW = "new"
    ACCEPTED = "accepted"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class Priority(Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class UserRole(Enum):
    """User roles for RBAC"""
    CUSTOMER_USER = "customer_user"
    CUSTOMER_ADMIN = "customer_admin"
    AGENT = "agent"
    MANAGER = "manager"
    ADMIN = "admin"


@dataclass(frozen=True)
class OrganizationId:
    """Value Object: Organization identifier"""
    value: UUID
    
    @classmethod
    def generate(cls) -> "OrganizationId":
        return cls(value=uuid4())
    
    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class UserId:
    """Value Object: User identifier"""
    value: UUID
    
    @classmethod
    def generate(cls) -> "UserId":
        return cls(value=uuid4())


@dataclass(frozen=True)
class TicketId:
    """Value Object: Ticket identifier"""
    value: UUID
    
    @classmethod
    def generate(cls) -> "TicketId":
        return cls(value=uuid4())


@dataclass(frozen=True)
class Email:
    """Value Object: Email address with validation"""
    value: str
    
    def __post_init__(self):
        if "@" not in self.value:
            raise ValueError(f"Invalid email: {self.value}")


@dataclass(frozen=True)
class Money:
    """Value Object: Monetary value"""
    amount: float
    currency: str = "USD"
    
    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)


@dataclass
class Organization:
    """Domain Entity: Organization (Aggregate Root)"""
    id: OrganizationId
    name: str
    slug: str
    domain: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def deactivate(self) -> None:
        """Business rule: Deactivate organization"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def update_name(self, new_name: str) -> None:
        """Business rule: Update organization name"""
        if not new_name or len(new_name) < 2:
            raise ValueError("Organization name must be at least 2 characters")
        self.name = new_name
        self.updated_at = datetime.utcnow()


@dataclass
class User:
    """Domain Entity: User (Aggregate Root)"""
    id: UserId
    organization_id: OrganizationId
    email: Email
    full_name: str
    role: UserRole
    is_active: bool = True
    email_verified: bool = False
    two_factor_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def has_permission(self, required_role: UserRole) -> bool:
        """Business rule: Check if user has required permission"""
        role_hierarchy = {
            UserRole.CUSTOMER_USER: 1,
            UserRole.CUSTOMER_ADMIN: 2,
            UserRole.AGENT: 3,
            UserRole.MANAGER: 4,
            UserRole.ADMIN: 5,
        }
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)
    
    def can_view_ticket(self, ticket_org_id: OrganizationId) -> bool:
        """Business rule: Multi-tenant isolation check"""
        return self.organization_id == ticket_org_id
    
    def enable_2fa(self) -> None:
        """Business rule: Enable two-factor authentication"""
        self.two_factor_enabled = True
        self.updated_at = datetime.utcnow()


@dataclass
class Comment:
    """Domain Entity: Comment (Value Object within Ticket)"""
    id: UUID = field(default_factory=uuid4)
    author_id: UserId = field(default=None)
    content: str = ""
    is_internal: bool = False
    is_ai_generated: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not self.content or len(self.content) < 1:
            raise ValueError("Comment content cannot be empty")


@dataclass
class Ticket:
    """Domain Entity: Ticket (Aggregate Root)"""
    id: TicketId
    organization_id: OrganizationId
    requester_id: UserId
    service_id: UUID
    subject: str
    description: str
    status: TicketStatus = TicketStatus.NEW
    priority: Priority = Priority.MEDIUM
    assigned_to: Optional[UserId] = None
    accepted_by: Optional[UserId] = None
    accepted_at: Optional[datetime] = None
    comments: List[Comment] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    # SLA tracking
    sla_due_at: Optional[datetime] = None
    sla_paused_at: Optional[datetime] = None
    sla_paused_duration: int = 0  # seconds
    
    def accept(self, manager_id: UserId) -> None:
        """Business rule: Manager accepts ticket"""
        if self.status != TicketStatus.NEW:
            raise ValueError(f"Cannot accept ticket in {self.status.value} status")
        self.status = TicketStatus.ACCEPTED
        self.accepted_by = manager_id
        self.accepted_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def assign(self, agent_id: UserId) -> None:
        """Business rule: Assign ticket to agent"""
        if self.status not in [TicketStatus.ACCEPTED, TicketStatus.NEW]:
            raise ValueError(f"Cannot assign ticket in {self.status.value} status")
        self.assigned_to = agent_id
        self.status = TicketStatus.ASSIGNED
        self.updated_at = datetime.utcnow()
    
    def add_comment(self, comment: Comment) -> None:
        """Business rule: Add comment to ticket"""
        self.comments.append(comment)
        self.updated_at = datetime.utcnow()
    
    def change_status(self, new_status: TicketStatus, user: User) -> None:
        """Business rule: Change ticket status with validation"""
        # Validate status transitions
        valid_transitions = {
            TicketStatus.NEW: [TicketStatus.ACCEPTED, TicketStatus.CANCELLED],
            TicketStatus.ACCEPTED: [TicketStatus.ASSIGNED, TicketStatus.CANCELLED],
            TicketStatus.ASSIGNED: [TicketStatus.IN_PROGRESS, TicketStatus.CANCELLED],
            TicketStatus.IN_PROGRESS: [TicketStatus.WAITING_CUSTOMER, TicketStatus.RESOLVED],
            TicketStatus.WAITING_CUSTOMER: [TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED],
            TicketStatus.RESOLVED: [TicketStatus.CLOSED, TicketStatus.IN_PROGRESS],
            TicketStatus.CLOSED: [],
            TicketStatus.CANCELLED: [],
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(
                f"Invalid status transition: {self.status.value} -> {new_status.value}"
            )
        
        # Handle SLA pause/resume
        if new_status == TicketStatus.WAITING_CUSTOMER:
            self.sla_paused_at = datetime.utcnow()
        elif self.status == TicketStatus.WAITING_CUSTOMER and new_status == TicketStatus.IN_PROGRESS:
            if self.sla_paused_at:
                paused_duration = (datetime.utcnow() - self.sla_paused_at).total_seconds()
                self.sla_paused_duration += int(paused_duration)
                self.sla_paused_at = None
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
        
        if new_status == TicketStatus.RESOLVED:
            self.resolved_at = datetime.utcnow()
        elif new_status == TicketStatus.CLOSED:
            self.closed_at = datetime.utcnow()
    
    def calculate_sla_deadline(self, response_time_minutes: int) -> datetime:
        """Business rule: Calculate SLA deadline considering business hours"""
        from datetime import timedelta
        
        base_time = self.accepted_at or self.created_at
        # Simplified: just add minutes (in real impl, consider business hours)
        return base_time + timedelta(minutes=response_time_minutes)


@dataclass
class SLAPolicy:
    """Domain Entity: SLA Policy (Aggregate Root)"""
    id: UUID = field(default_factory=uuid4)
    organization_id: OrganizationId = field(default=None)
    name: str = ""
    response_time_low: int = 240  # minutes
    response_time_medium: int = 120
    response_time_high: int = 60
    response_time_urgent: int = 15
    resolution_time_low: int = 2880  # 48 hours
    resolution_time_medium: int = 1440  # 24 hours
    resolution_time_high: int = 480  # 8 hours
    resolution_time_urgent: int = 240  # 4 hours
    business_hours_enabled: bool = False
    timezone: str = "UTC"
    is_active: bool = True
    
    def get_response_time(self, priority: Priority) -> int:
        """Business rule: Get response time for priority"""
        times = {
            Priority.LOW: self.response_time_low,
            Priority.MEDIUM: self.response_time_medium,
            Priority.HIGH: self.response_time_high,
            Priority.URGENT: self.response_time_urgent,
        }
        return times.get(priority, self.response_time_medium)
    
    def get_resolution_time(self, priority: Priority) -> int:
        """Business rule: Get resolution time for priority"""
        times = {
            Priority.LOW: self.resolution_time_low,
            Priority.MEDIUM: self.resolution_time_medium,
            Priority.HIGH: self.resolution_time_high,
            Priority.URGENT: self.resolution_time_urgent,
        }
        return times.get(priority, self.resolution_time_medium)


@dataclass
class Attachment:
    """Domain Entity: File Attachment (Value Object)"""
    id: UUID = field(default_factory=uuid4)
    ticket_id: TicketId = field(default=None)
    filename: str = ""
    file_path: str = ""
    file_size: int = 0
    mime_type: str = ""
    file_hash: str = ""  # SHA-256
    uploaded_by: UserId = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def verify_integrity(self) -> bool:
        """Business rule: Verify file integrity using hash"""
        # Implementation would check file hash
        return True


@dataclass
class KBArticle:
    """Domain Entity: Knowledge Base Article (Aggregate Root)"""
    id: UUID = field(default_factory=uuid4)
    organization_id: OrganizationId = field(default=None)
    category_id: Optional[UUID] = None
    title: str = ""
    slug: str = ""
    content: str = ""
    excerpt: str = ""
    is_internal: bool = False
    is_published: bool = False
    view_count: int = 0
    helpful_count: int = 0
    unhelpful_count: int = 0
    created_by: UserId = field(default=None)
    updated_by: Optional[UserId] = None
    published_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def publish(self, user_id: UserId) -> None:
        """Business rule: Publish article"""
        self.is_published = True
        self.published_at = datetime.utcnow()
        self.updated_by = user_id
        self.updated_at = datetime.utcnow()
    
    def increment_view(self) -> None:
        """Business rule: Track view"""
        self.view_count += 1
    
    def mark_helpful(self) -> None:
        """Business rule: Mark as helpful"""
        self.helpful_count += 1
    
    def mark_unhelpful(self) -> None:
        """Business rule: Mark as unhelpful"""
        self.unhelpful_count += 1


@dataclass
class CannedResponse:
    """Domain Entity: Canned Response (Aggregate Root)"""
    id: UUID = field(default_factory=uuid4)
    organization_id: OrganizationId = field(default=None)
    title: str = ""
    content: str = ""
    shortcut: str = ""  # e.g., "/greeting"
    category: str = ""
    is_personal: bool = False
    created_by: UserId = field(default=None)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def render(self, variables: dict) -> str:
        """Business rule: Render template with variables"""
        result = self.content
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result


@dataclass
class TimeEntry:
    """Domain Entity: Time Tracking Entry (Value Object)"""
    id: UUID = field(default_factory=uuid4)
    ticket_id: TicketId = field(default=None)
    user_id: UserId = field(default=None)
    duration_minutes: int = 0
    description: str = ""
    is_billable: bool = True
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def stop(self) -> None:
        """Business rule: Stop time tracking"""
        self.ended_at = datetime.utcnow()
    
    def get_duration_hours(self) -> float:
        """Business rule: Get duration in hours"""
        if self.ended_at:
            duration = self.ended_at - self.started_at
            return duration.total_seconds() / 3600
        return 0.0


@dataclass
class CSATSurvey:
    """Domain Entity: Customer Satisfaction Survey (Value Object)"""
    id: UUID = field(default_factory=uuid4)
    ticket_id: TicketId = field(default=None)
    rating: int = 0  # 1-5
    comment: str = ""
    respondent_email: str = ""
    is_internal: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        if not 1 <= self.rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
    
    def is_positive(self) -> bool:
        """Business rule: Check if rating is positive (4-5)"""
        return self.rating >= 4
