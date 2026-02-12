"""
ATUM DESK - Unit Tests for Domain Layer
Following Testing Pyramid: Unit → Integration → E2E
"""
import pytest
from datetime import datetime
from uuid import uuid4

from src.domain.entities import (
    Ticket, TicketId, TicketStatus,
    User, UserId, UserRole,
    Organization, OrganizationId,
    Email, Comment, Priority,
    SLAPolicy,
)


class TestTicketEntity:
    """Unit tests for Ticket domain entity"""
    
    def test_create_ticket(self):
        """Test: Ticket can be created with valid data"""
        # Arrange
        org_id = OrganizationId.generate()
        requester_id = UserId.generate()
        service_id = uuid4()
        
        # Act
        ticket = Ticket(
            id=TicketId.generate(),
            organization_id=org_id,
            requester_id=requester_id,
            service_id=service_id,
            subject="Test Subject",
            description="Test Description",
        )
        
        # Assert
        assert ticket.status == TicketStatus.NEW
        assert ticket.priority == Priority.MEDIUM
        assert ticket.subject == "Test Subject"
        assert ticket.organization_id == org_id
    
    def test_accept_ticket(self):
        """Test: Manager can accept NEW ticket"""
        # Arrange
        ticket = self._create_new_ticket()
        manager_id = UserId.generate()
        
        # Act
        ticket.accept(manager_id)
        
        # Assert
        assert ticket.status == TicketStatus.ACCEPTED
        assert ticket.accepted_by == manager_id
        assert ticket.accepted_at is not None
    
    def test_cannot_accept_non_new_ticket(self):
        """Test: Cannot accept ticket that is not NEW"""
        # Arrange
        ticket = self._create_new_ticket()
        manager_id = UserId.generate()
        ticket.accept(manager_id)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot accept ticket"):
            ticket.accept(manager_id)
    
    def test_assign_ticket(self):
        """Test: Can assign ACCEPTED ticket to agent"""
        # Arrange
        ticket = self._create_new_ticket()
        manager_id = UserId.generate()
        agent_id = UserId.generate()
        ticket.accept(manager_id)
        
        # Act
        ticket.assign(agent_id)
        
        # Assert
        assert ticket.status == TicketStatus.ASSIGNED
        assert ticket.assigned_to == agent_id
    
    def test_change_status_valid_transition(self):
        """Test: Valid status transition works"""
        # Arrange
        ticket = self._create_new_ticket()
        manager_id = UserId.generate()
        ticket.accept(manager_id)
        
        user = User(
            id=manager_id,
            organization_id=ticket.organization_id,
            email=Email("manager@test.com"),
            full_name="Manager",
            role=UserRole.MANAGER,
        )
        
        # Act
        ticket.change_status(TicketStatus.IN_PROGRESS, user)
        
        # Assert
        assert ticket.status == TicketStatus.IN_PROGRESS
    
    def test_change_status_invalid_transition(self):
        """Test: Invalid status transition raises error"""
        # Arrange
        ticket = self._create_new_ticket()
        user = User(
            id=UserId.generate(),
            organization_id=ticket.organization_id,
            email=Email("user@test.com"),
            full_name="User",
            role=UserRole.AGENT,
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid status transition"):
            ticket.change_status(TicketStatus.CLOSED, user)
    
    def test_add_comment(self):
        """Test: Can add comment to ticket"""
        # Arrange
        ticket = self._create_new_ticket()
        author_id = UserId.generate()
        
        comment = Comment(
            author_id=author_id,
            content="Test comment",
            is_internal=False,
        )
        
        # Act
        ticket.add_comment(comment)
        
        # Assert
        assert len(ticket.comments) == 1
        assert ticket.comments[0].content == "Test comment"
    
    def test_sla_pause_on_waiting_customer(self):
        """Test: SLA pauses when status changes to WAITING_CUSTOMER"""
        # Arrange
        ticket = self._create_new_ticket()
        ticket.accepted_at = datetime.utcnow()
        ticket.sla_due_at = datetime.utcnow()
        
        user = User(
            id=UserId.generate(),
            organization_id=ticket.organization_id,
            email=Email("agent@test.com"),
            full_name="Agent",
            role=UserRole.AGENT,
        )
        ticket.accept(user.id)
        ticket.assign(user.id)
        
        # Act
        ticket.change_status(TicketStatus.WAITING_CUSTOMER, user)
        
        # Assert
        assert ticket.sla_paused_at is not None
    
    def _create_new_ticket(self) -> Ticket:
        """Helper: Create a new ticket for testing"""
        return Ticket(
            id=TicketId.generate(),
            organization_id=OrganizationId.generate(),
            requester_id=UserId.generate(),
            service_id=uuid4(),
            subject="Test Ticket",
            description="Test Description",
        )


class TestUserEntity:
    """Unit tests for User domain entity"""
    
    def test_has_permission_hierarchy(self):
        """Test: User role hierarchy works correctly"""
        # Arrange
        admin = self._create_user(UserRole.ADMIN)
        manager = self._create_user(UserRole.MANAGER)
        agent = self._create_user(UserRole.AGENT)
        customer = self._create_user(UserRole.CUSTOMER_USER)
        
        # Assert - Admin can do everything
        assert admin.has_permission(UserRole.ADMIN)
        assert admin.has_permission(UserRole.MANAGER)
        assert admin.has_permission(UserRole.AGENT)
        
        # Manager can do manager, agent, customer tasks
        assert manager.has_permission(UserRole.MANAGER)
        assert manager.has_permission(UserRole.AGENT)
        assert not manager.has_permission(UserRole.ADMIN)
        
        # Agent can do agent and customer tasks
        assert agent.has_permission(UserRole.AGENT)
        assert not agent.has_permission(UserRole.MANAGER)
        
        # Customer can only do customer tasks
        assert customer.has_permission(UserRole.CUSTOMER_USER)
        assert not customer.has_permission(UserRole.AGENT)
    
    def test_can_view_ticket_same_org(self):
        """Test: User can view tickets from same organization"""
        # Arrange
        org_id = OrganizationId.generate()
        user = User(
            id=UserId.generate(),
            organization_id=org_id,
            email=Email("user@test.com"),
            full_name="User",
            role=UserRole.CUSTOMER_USER,
        )
        
        # Act & Assert
        assert user.can_view_ticket(org_id) is True
    
    def test_cannot_view_ticket_different_org(self):
        """Test: User cannot view tickets from different organization"""
        # Arrange
        user_org = OrganizationId.generate()
        ticket_org = OrganizationId.generate()
        
        user = User(
            id=UserId.generate(),
            organization_id=user_org,
            email=Email("user@test.com"),
            full_name="User",
            role=UserRole.CUSTOMER_USER,
        )
        
        # Act & Assert
        assert user.can_view_ticket(ticket_org) is False
    
    def test_enable_2fa(self):
        """Test: User can enable 2FA"""
        # Arrange
        user = self._create_user(UserRole.CUSTOMER_USER)
        assert user.two_factor_enabled is False
        
        # Act
        user.enable_2fa()
        
        # Assert
        assert user.two_factor_enabled is True
    
    def test_invalid_email_raises_error(self):
        """Test: Invalid email raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email"):
            Email("invalid-email")
    
    def _create_user(self, role: UserRole) -> User:
        """Helper: Create a user for testing"""
        return User(
            id=UserId.generate(),
            organization_id=OrganizationId.generate(),
            email=Email(f"user_{role.value}@test.com"),
            full_name=f"Test {role.value}",
            role=role,
        )


class TestSLAPolicyEntity:
    """Unit tests for SLA Policy domain entity"""
    
    def test_get_response_time_by_priority(self):
        """Test: Get response time for each priority level"""
        # Arrange
        policy = SLAPolicy(
            name="Standard SLA",
            response_time_low=240,      # 4 hours
            response_time_medium=120,   # 2 hours
            response_time_high=60,      # 1 hour
            response_time_urgent=15,    # 15 minutes
        )
        
        # Act & Assert
        assert policy.get_response_time(Priority.LOW) == 240
        assert policy.get_response_time(Priority.MEDIUM) == 120
        assert policy.get_response_time(Priority.HIGH) == 60
        assert policy.get_response_time(Priority.URGENT) == 15
    
    def test_get_resolution_time_by_priority(self):
        """Test: Get resolution time for each priority level"""
        # Arrange
        policy = SLAPolicy(
            name="Standard SLA",
            resolution_time_low=2880,     # 48 hours
            resolution_time_medium=1440,  # 24 hours
            resolution_time_high=480,     # 8 hours
            resolution_time_urgent=240,   # 4 hours
        )
        
        # Act & Assert
        assert policy.get_resolution_time(Priority.LOW) == 2880
        assert policy.get_resolution_time(Priority.MEDIUM) == 1440
        assert policy.get_resolution_time(Priority.HIGH) == 480
        assert policy.get_resolution_time(Priority.URGENT) == 240


class TestOrganizationEntity:
    """Unit tests for Organization domain entity"""
    
    def test_deactivate_organization(self):
        """Test: Can deactivate organization"""
        # Arrange
        org = Organization(
            id=OrganizationId.generate(),
            name="Test Org",
            slug="test-org",
            is_active=True,
        )
        
        # Act
        org.deactivate()
        
        # Assert
        assert org.is_active is False
    
    def test_update_name(self):
        """Test: Can update organization name"""
        # Arrange
        org = Organization(
            id=OrganizationId.generate(),
            name="Old Name",
            slug="test-org",
        )
        
        # Act
        org.update_name("New Name")
        
        # Assert
        assert org.name == "New Name"
    
    def test_update_name_too_short_raises_error(self):
        """Test: Updating name with too short value raises error"""
        # Arrange
        org = Organization(
            id=OrganizationId.generate(),
            name="Test Org",
            slug="test-org",
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="at least 2 characters"):
            org.update_name("A")


class TestValueObjects:
    """Unit tests for value objects"""
    
    def test_email_creation(self):
        """Test: Valid email can be created"""
        email = Email("test@example.com")
        assert email.value == "test@example.com"
    
    def test_email_validation(self):
        """Test: Invalid email raises error"""
        with pytest.raises(ValueError):
            Email("not-an-email")
    
    def test_ticket_id_generation(self):
        """Test: TicketId generates unique UUIDs"""
        id1 = TicketId.generate()
        id2 = TicketId.generate()
        assert id1.value != id2.value
