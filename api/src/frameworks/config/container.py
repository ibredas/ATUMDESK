"""
Dependency Injection Container
Implements Dependency Inversion Principle
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.domain.repositories import (
    ITicketRepository,
    IUserRepository,
    IOrganizationRepository,
)
from src.interface_adapters.repositories_impl.sqlalchemy import (
    SQLAlchemyTicketRepository,
    SQLAlchemyUserRepository,
)
from src.usecases.ticket import (
    CreateTicketUseCase,
    AcceptTicketUseCase,
    AssignTicketUseCase,
    ChangeTicketStatusUseCase,
    AddCommentUseCase,
)


class Container:
    """
    Dependency Injection Container
    Manages all dependencies and their lifecycles
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self._engine = None
        self._session_maker = None
    
    def init_engine(self):
        """Initialize database engine"""
        self._engine = create_async_engine(
            self.database_url,
            echo=False,
            future=True,
        )
        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup"""
        session = self._session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # Repository Factory Methods
    
    async def get_ticket_repository(self) -> AsyncGenerator[ITicketRepository, None]:
        """Factory: Ticket Repository"""
        async with self.get_session() as session:
            yield SQLAlchemyTicketRepository(session)
    
    async def get_user_repository(self) -> AsyncGenerator[IUserRepository, None]:
        """Factory: User Repository"""
        async with self.get_session() as session:
            yield SQLAlchemyUserRepository(session)
    
    # Use Case Factory Methods
    
    async def get_create_ticket_use_case(self) -> AsyncGenerator[CreateTicketUseCase, None]:
        """Factory: Create Ticket Use Case"""
        async with self.get_session() as session:
            ticket_repo = SQLAlchemyTicketRepository(session)
            user_repo = SQLAlchemyUserRepository(session)
            # For SLA repo, use same pattern
            from src.interface_adapters.repositories_impl.sqlalchemy.sla_repository import SQLAlchemySLARepository
            sla_repo = SQLAlchemySLARepository(session)
            
            yield CreateTicketUseCase(
                ticket_repo=ticket_repo,
                user_repo=user_repo,
                sla_repo=sla_repo,
            )
    
    async def get_accept_ticket_use_case(self) -> AsyncGenerator[AcceptTicketUseCase, None]:
        """Factory: Accept Ticket Use Case"""
        async with self.get_session() as session:
            ticket_repo = SQLAlchemyTicketRepository(session)
            user_repo = SQLAlchemyUserRepository(session)
            
            yield AcceptTicketUseCase(
                ticket_repo=ticket_repo,
                user_repo=user_repo,
            )
    
    async def get_assign_ticket_use_case(self) -> AsyncGenerator[AssignTicketUseCase, None]:
        """Factory: Assign Ticket Use Case"""
        async with self.get_session() as session:
            ticket_repo = SQLAlchemyTicketRepository(session)
            user_repo = SQLAlchemyUserRepository(session)
            
            yield AssignTicketUseCase(
                ticket_repo=ticket_repo,
                user_repo=user_repo,
            )
    
    async def get_change_status_use_case(self) -> AsyncGenerator[ChangeTicketStatusUseCase, None]:
        """Factory: Change Status Use Case"""
        async with self.get_session() as session:
            ticket_repo = SQLAlchemyTicketRepository(session)
            user_repo = SQLAlchemyUserRepository(session)
            
            yield ChangeTicketStatusUseCase(
                ticket_repo=ticket_repo,
                user_repo=user_repo,
            )
    
    async def get_add_comment_use_case(self) -> AsyncGenerator[AddCommentUseCase, None]:
        """Factory: Add Comment Use Case"""
        async with self.get_session() as session:
            ticket_repo = SQLAlchemyTicketRepository(session)
            user_repo = SQLAlchemyUserRepository(session)
            
            yield AddCommentUseCase(
                ticket_repo=ticket_repo,
                user_repo=user_repo,
            )


# Global container instance (will be initialized in main)
container: Container = None


def init_container(database_url: str):
    """Initialize global container"""
    global container
    container = Container(database_url)
    container.init_engine()
    return container


def get_container() -> Container:
    """Get global container"""
    if container is None:
        raise RuntimeError("Container not initialized. Call init_container first.")
    return container
