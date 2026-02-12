# Architecture Decision Record (ADR): Clean Architecture for ATUM DESK

**Status**: ACCEPTED  
**Date**: 2026-02-12  
**Author**: ATUM DESK Development Team  
**Decision ID**: ADR-001

---

## Context

ATUM DESK is a production-grade helpdesk/ticketing platform with the following characteristics:
- **Complexity**: 14 enhanced features including AI integration, SLA management, multi-tenancy
- **Scale**: Needs to handle 100+ concurrent users
- **Longevity**: Expected to evolve over years with new features
- **Team**: Multiple developers will work on the codebase
- **Quality Requirements**: High testability, maintainability, scalability

We needed to choose an architecture that supports:
1. Business logic independent of frameworks
2. Easy testing at all levels
3. Clear separation of concerns
4. Ability to change technologies without rewriting business logic
5. Domain-Driven Design principles

---

## Decision

**We will implement ATUM DESK using Clean Architecture (Onion/Hexagonal Architecture)** as described by Robert C. Martin (Uncle Bob).

### Architecture Structure

```
atum-desk/api/src/
├── domain/                    # Innermost layer - pure business logic
│   ├── entities/              # Domain entities (Ticket, User, etc.)
│   ├── repositories/          # Repository interfaces (abstract)
│   ├── services/              # Domain services
│   └── events/                # Domain events
│
├── usecases/                  # Application business rules
│   ├── ticket/                # Ticket use cases
│   ├── auth/                  # Authentication use cases
│   ├── user/                  # User management use cases
│   └── ...                    # Other use cases
│
├── interface_adapters/        # Adapters for external interfaces
│   ├── controllers/           # HTTP/API controllers
│   ├── presenters/            # Response formatters
│   ├── gateways/              # External service gateways
│   └── repositories_impl/     # Repository implementations
│       ├── sqlalchemy/        # SQLAlchemy implementations
│       └── redis/             # Redis implementations
│
└── frameworks/                # External frameworks (outermost layer)
    ├── fastapi/               # FastAPI web framework
    ├── sqlalchemy/            # ORM setup
    ├── celery/                # Background tasks
    └── config/                # Configuration
```

### Dependency Rule

**Dependencies point INWARD only:**
- Domain layer has NO dependencies on other layers
- Use cases depend ONLY on domain
- Interface adapters depend on domain and use cases
- Frameworks depend on all inner layers

---

## Consequences

### Positive

1. **Framework Independence**
   - Can switch from FastAPI to Django/Flask without touching domain logic
   - Can change database from PostgreSQL to MongoDB by implementing new repositories
   - Framework changes don't break business rules

2. **High Testability**
   - Domain logic can be tested without database, HTTP, or external services
   - Use cases can be tested with mocked repositories
   - Unit tests run in milliseconds
   - Test coverage can approach 100% for business logic

3. **Clear Separation of Concerns**
   - Domain: Pure business logic, no technical details
   - Use Cases: Application workflow orchestration
   - Interface Adapters: Data conversion and delivery
   - Frameworks: Technical implementation details

4. **Maintainability**
   - Easy to locate where changes need to be made
   - Business logic is centralized and obvious
   - No "hidden" business rules in controllers or database queries

5. **Domain-Driven Design Support**
   - Entities encapsulate business rules
   - Value objects ensure data integrity
   - Repository pattern abstracts persistence
   - Use cases represent user stories

6. **Team Scalability**
   - Junior developers can work on outer layers (controllers, UI)
   - Senior developers focus on domain and use cases
   - Clear contracts between layers via interfaces

### Negative

1. **Initial Complexity**
   - More boilerplate code than simple CRUD
   - More files and directories to navigate
   - Steeper learning curve for new team members

2. **Overhead for Simple Operations**
   - Creating a simple CRUD endpoint requires:
     - Domain entity
     - Repository interface
     - Use case
     - Repository implementation
     - Controller
   - This can feel like overkill for trivial operations

3. **Performance Considerations**
   - Additional layers add slight overhead
   - Mapping between layers requires CPU cycles
   - Memory usage increases with multiple object representations

4. **Developer Discipline Required**
   - Easy to violate dependency rule if not careful
   - Must resist temptation to take shortcuts
   - Code reviews must enforce architecture compliance

---

## Alternatives Considered

### 1. Traditional Layered Architecture (MVC)
**Rejected**: Business logic mixed with framework code, difficult to test, framework coupling

### 2. Simple CRUD/Transaction Script
**Rejected**: No separation of concerns, business logic scattered, hard to maintain as complexity grows

### 3. Microservices
**Rejected**: Unnecessary complexity for initial scope, deployment overhead, network latency

### 4. Serverless Functions
**Rejected**: Cold start issues, vendor lock-in, state management complexity

---

## Implementation Details

### SOLID Principles Applied

**Single Responsibility Principle (SRP)**
- Each class has one reason to change
- Entities: business rules
- Repositories: data access
- Use cases: workflow
- Controllers: HTTP handling

**Open/Closed Principle (OCP)**
- Open for extension, closed for modification
- New use cases can be added without changing existing ones
- New repository implementations for different databases

**Liskov Substitution Principle (LSP)**
- Repository implementations are interchangeable
- SQLAlchemyRepository can be replaced with MongoRepository
- All tests still pass

**Interface Segregation Principle (ISP)**
- Repository interfaces are focused
- ITicketRepository doesn't force methods for unrelated entities
- Controllers only depend on use cases they need

**Dependency Inversion Principle (DIP)**
- High-level modules (use cases) don't depend on low-level modules (repositories)
- Both depend on abstractions (interfaces)
- Dependency injection container manages wiring

### Design Patterns Used

1. **Repository Pattern**: Abstract data access
2. **Unit of Work**: Transaction management via SQLAlchemy session
3. **Dependency Injection**: Container manages object lifecycle
4. **DTO (Data Transfer Objects)**: Request/response objects for use cases
5. **Factory Pattern**: Container factory methods for repositories and use cases

### Testing Strategy

**Unit Tests** (test domain and use cases)
- No database, no HTTP server
- Mocked repositories
- Fast execution (< 10ms per test)

**Integration Tests** (test repositories)
- Real database (testcontainers)
- Verify SQL and mapping correctness

**E2E Tests** (test full flow)
- HTTP client makes real requests
- Database is populated
- Verify end-to-end behavior

---

## Compliance Verification

To verify this ADR is being followed:

1. **Import Checks**
   - Domain should NOT import from usecases, interface_adapters, or frameworks
   - Use cases should NOT import from interface_adapters or frameworks
   - Interface adapters should NOT import from frameworks

2. **Dependency Direction**
   ```bash
   # Check for violations
   grep -r "from src.frameworks" src/domain/
   grep -r "from src.frameworks" src/usecases/
   grep -r "from src.interface_adapters" src/domain/
   ```

3. **Test Independence**
   - Domain tests should run without pytest-django, pytest-flask, etc.
   - No database setup required for domain/use case tests

---

## Migration Path

If we need to migrate away from this architecture:

1. **To Microservices**: Extract bounded contexts from domain layer
2. **To Different Framework**: Replace frameworks layer, keep domain and use cases
3. **To Different Database**: Implement new repository implementations

---

## References

- Clean Architecture by Robert C. Martin
- Domain-Driven Design by Eric Evans
- Hexagonal Architecture by Alistair Cockburn
- Microsoft: Common web application architectures

---

## Decision Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2026-02-12 | 1.0 | Initial decision to use Clean Architecture | ATUM Team |

---

**Approved By**: Pharaoh Navi (Ibreda)  
**Next Review**: After 6 months or when major feature added
