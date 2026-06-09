---
name: ddd-context-mapping
description: >
  Use this skill whenever a task involves designing or decomposing a system using Domain-Driven Design (DDD).
  Triggers include: defining bounded contexts, identifying aggregates/entities/value objects, mapping context
  relationships (ACL, shared kernel, upstream/downstream), splitting a monolith into services, creating
  ubiquitous language glossaries, modeling domain events, or deciding service boundaries. Also triggers when
  the user asks about "domain", "context", "aggregate", "bounded context", "domain events", "DDD", or
  "context map". Apply before writing any service or module code so boundaries are established first.
---

# DDD Context Mapping & Domain Separation

Act as a principal software architect with deep DDD expertise. Before writing any code or module structure,
establish the domain model explicitly. Ambiguous boundaries cause coupling debt — resolve them here first.

---

## Phase 1 — Strategic Design (Do This First)

### 1.1 Problem Space Exploration

Always start by asking (or inferring from context):
- What is the **core domain**? (the unique business value — invest the most here)
- What are the **supporting subdomains**? (necessary but not differentiating)
- What are the **generic subdomains**? (commodity — use off-the-shelf when possible)

Document as:
```
Core Domain:       [Name] — [one-sentence business purpose]
Supporting:        [Name], [Name]
Generic:           [Name] (→ use [library/service])
```

### 1.2 Bounded Context Identification

For each major capability cluster, define a Bounded Context:

```
Bounded Context: [Name]
  Purpose:       [What problem this context solves]
  Owns:          [Data and processes it is authoritative over]
  Language:      [Key ubiquitous language terms — 3 to 8 nouns]
  Team:          [Owning team or squad, if known]
  Exposed via:   [API / Event / None]
```

Rules:
- One team per context (Conway's Law applies)
- A term means ONE thing inside one context; it may mean something else in another
- Never share a database across contexts — share via API or events only
- A context is too large if it has more than ~8 aggregates; split it

### 1.3 Context Map

Draw relationships between bounded contexts. Use these patterns:

| Pattern | Symbol | Meaning |
|---|---|---|
| Partnership | `<->` | Teams coordinate; shared success/failure |
| Shared Kernel | `SK` | Small shared model; both teams must approve changes |
| Customer/Supplier | `U → D` | Upstream provides; downstream consumes |
| Conformist | `D conforms` | Downstream adopts upstream model as-is |
| Anti-Corruption Layer | `ACL` | Downstream translates upstream to own model |
| Open Host Service | `OHS` | Upstream publishes a stable protocol |
| Published Language | `PL` | Shared, documented exchange format (e.g. CloudEvents) |
| Separate Ways | `//` | No integration; contexts solve independently |

Example map output:
```
[Orders] U──OHS/PL──▶ [Inventory] (ACL) ──▶ [Shipping]
             ↑
         [Catalog] SK ── [Pricing]
```

---

## Phase 2 — Tactical Design

### 2.1 Aggregate Design Rules

An **Aggregate** is a cluster of objects treated as a unit for data changes.

```go
// Aggregate root example skeleton
type Order struct {                  // Aggregate Root
    id         OrderID               // Identity — always a Value Object
    status     OrderStatus
    items       []OrderItem          // Entities owned by this aggregate
    totalAmount Money                // Value Object
    events     []DomainEvent        // Uncommitted domain events
}
```

Rules:
- Only the **Aggregate Root** has a globally unique identity
- External objects reference Aggregates by root ID only (no direct child references)
- Aggregates should be **small** — prefer many small aggregates over large ones
- One transaction = one aggregate (use eventual consistency across aggregates)
- Keep invariants **inside** the aggregate; do not leak validation to services

### 2.2 Domain Events

Domain events are the truth record of what happened.

```go
// DomainEvent is the interface all domain events must implement.
type DomainEvent interface {
    AggregateID() string
    EventType()   string
    OccurredAt()  time.Time
    EventVersion() int
}
```

Naming: always past tense — `OrderPlaced`, `PaymentFailed`, `InventoryReserved`

Checklist per event:
- [ ] Named in past tense
- [ ] Contains only data available at time of occurrence
- [ ] Is immutable (no setters)
- [ ] Has a schema version field
- [ ] Is published **after** the aggregate is persisted (outbox pattern)

### 2.3 Value Objects

Encapsulate domain concepts that have no identity:

```go
// Money is a Value Object representing a monetary amount with currency.
// Two Money values are equal when both Amount and Currency match.
type Money struct {
    amount   int64  // minor units (cents)
    currency string // ISO 4217
}

func NewMoney(amount int64, currency string) (Money, error) { ... }
func (m Money) Add(other Money) (Money, error)              { ... }
func (m Money) Equals(other Money) bool                     { ... }
```

Rules:
- No ID field
- Immutable — all methods return new value objects
- Validation in constructor; never produce invalid state
- Implement `Equals()` by value, not reference

### 2.4 Repository Interfaces

Define in the domain layer; implement in infrastructure:

```go
// OrderRepository defines the persistence contract for the Order aggregate.
// Implementations live in the infrastructure layer and must not leak ORM details.
type OrderRepository interface {
    FindByID(ctx context.Context, id OrderID) (*Order, error)
    Save(ctx context.Context, order *Order) error
    NextIdentity() OrderID
}
```

---

## Phase 3 — Context Integration Patterns

### When contexts must communicate, choose:

**Synchronous (request/response):**
- Use when the caller needs an immediate answer to proceed
- Implement with REST or gRPC with circuit breaker + retry
- Apply ACL in the consuming context to translate models

**Asynchronous (event-driven):**
- Use when the caller does not need an immediate answer
- Publish domain events to a broker (SNS/SQS, Kafka, EventBridge)
- Consumer applies ACL to map event schema to its own model
- Use the **Outbox Pattern** to guarantee at-least-once delivery

**Anti-Corruption Layer (ACL) example:**
```go
// OrderACL translates upstream Catalog context DTOs into local domain types.
// Never expose upstream types beyond this boundary.
type OrderACL struct{ catalogClient catalog.Client }

func (a *OrderACL) GetProduct(ctx context.Context, id string) (domain.Product, error) {
    raw, err := a.catalogClient.FindProduct(ctx, id)   // upstream type
    if err != nil { return domain.Product{}, mapCatalogError(err) }
    return domain.Product{                              // local type
        ID:    domain.ProductID(raw.SKU),
        Name:  raw.Title,
        Price: domain.NewMoneyFromCents(raw.PriceCents, raw.Currency),
    }, nil
}
```

---

## Phase 4 — Output Checklist

Before handing off to implementation, verify:

- [ ] Core / Supporting / Generic subdomains identified
- [ ] Each bounded context has a single owning team and clear purpose
- [ ] Ubiquitous language glossary exists per context (≥ 5 terms)
- [ ] Context map drawn with explicit integration patterns
- [ ] Each aggregate has a clear root and invariant list
- [ ] Domain events named in past tense with schema version
- [ ] Repository interfaces defined in domain, not infrastructure
- [ ] No shared databases between contexts
- [ ] ACL exists wherever a context consumes another context's model

---

## Anti-Patterns to Reject

| Anti-Pattern | Why Bad | Fix |
|---|---|---|
| Anemic domain model | Business logic leaks to services; domain is just DTOs | Move invariants and behavior into aggregates |
| Shared database | Tight coupling; blocks independent deployment | Use events or APIs; each context owns its schema |
| God aggregate | Contention, huge transactions, slow tests | Split into smaller aggregates with eventual consistency |
| Leaking upstream types | Context polluted by foreign model changes | Introduce ACL; translate at the boundary |
| Skipping ubiquitous language | Misunderstandings baked into code | Define glossary first; align with domain experts |
