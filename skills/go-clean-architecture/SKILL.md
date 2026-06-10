---
name: go-clean-architecture
description: >
  Use this skill whenever writing Go code that must follow Clean Architecture (also known as Hexagonal /
  Ports & Adapters). Triggers include: creating a new Go service or module, structuring Go project directories,
  designing use cases / application services, separating domain from infrastructure, wiring dependency injection
  in Go, or any task where the user mentions "clean architecture", "hexagonal", "ports and adapters", "use case",
  "adapter", "repository pattern" in Go context. Always apply before generating Go service scaffolding.
---

# Go Clean Architecture

Apply the Clean Architecture strictly and consistently. The prime directive: **inner layers never import outer layers**.
Violations break testability, deployability, and replaceability — refuse to generate code that crosses boundaries inward.

---

## Layer Model

```
┌──────────────────────────────────────────────┐
│              Frameworks & Drivers            │  ← HTTP handlers, gRPC, CLI, Lambda handler
│  (infrastructure/adapters/in)               │
├──────────────────────────────────────────────┤
│           Interface Adapters                 │  ← Controllers, presenters, ACL, DTOs
│  (internal/adapters)                        │
├──────────────────────────────────────────────┤
│           Application / Use Cases            │  ← Orchestrates domain; owns transactions
│  (internal/application)                     │
├──────────────────────────────────────────────┤
│                 Domain                       │  ← Entities, value objects, domain events
│  (internal/domain)                          │     repository interfaces, domain services
└──────────────────────────────────────────────┘
         ↑ Dependency direction (inward only)
```

---

## Canonical Directory Layout

```
service-name/
├── cmd/
│   └── api/
│       └── main.go                  # Wire everything; start server
├── internal/
│   ├── domain/
│   │   ├── model/                   # Aggregates, entities, value objects
│   │   ├── event/                   # Domain events
│   │   ├── repository/              # Repository interfaces (ports)
│   │   └── service/                 # Domain services (stateless logic)
│   ├── application/
│   │   ├── usecase/                 # One file per use case
│   │   ├── port/
│   │   │   ├── input/               # Input port interfaces (driven by adapters/in)
│   │   │   └── output/              # Output port interfaces (implemented by adapters/out)
│   │   └── dto/                     # Application-layer data transfer objects
│   └── adapter/
│       ├── in/
│       │   ├── http/                # Chi/Echo/Gin handlers → call input ports
│       │   ├── grpc/                # gRPC server implementations
│       │   └── lambda/              # AWS Lambda event handlers
│       └── out/
│           ├── persistence/         # DynamoDB, RDS, ElastiCache implementations
│           ├── messaging/           # SNS, SQS, EventBridge publishers
│           └── external/            # HTTP clients for external services (with ACL)
├── pkg/                             # Truly shared, zero-domain packages (errors, tracing, etc.)
├── configs/                         # YAML / env config structs
├── deployments/                     # Terraform, SAM, CDK
└── docs/                            # ADRs, OpenAPI specs
```

---

## Domain Layer Rules

```go
// Package domain contains the core business entities and rules for the Orders bounded context.
// This package MUST NOT import any infrastructure or framework packages.
// It is the innermost layer and has zero external dependencies.
package domain

// Order is the aggregate root for the order lifecycle.
// It enforces all invariants related to order state transitions.
// All mutations return domain events to be published after persistence.
type Order struct {
    id     OrderID
    status OrderStatus
    items  []OrderItem
    total  Money
    events []DomainEvent
}

// Place transitions a new Order to the Placed state.
// Returns ErrInvalidOrder if items is empty or total is zero.
func (o *Order) Place() error {
    if len(o.items) == 0 {
        return ErrInvalidOrder{Reason: "order must have at least one item"}
    }
    o.status = StatusPlaced
    o.recordEvent(OrderPlaced{OrderID: o.id, OccurredAt: time.Now()})
    return nil
}

// DomainEvents returns uncommitted events and clears the internal buffer.
// Call this after Save() to publish events.
func (o *Order) DomainEvents() []DomainEvent {
    evts := o.events
    o.events = nil
    return evts
}
```

**Domain layer rules:**
- No `import` of `database/sql`, `net/http`, AWS SDK, or any framework
- No struct tags (`json`, `db`) — those belong in DTOs or persistence structs
- All errors are domain-typed (`ErrNotFound`, `ErrInvalidOrder`), not generic
- Domain services handle logic that spans multiple aggregates

---

## Application Layer (Use Cases)

```go
// Package usecase implements the application use cases for the Orders context.
// Each use case orchestrates domain objects and calls output ports.
// It must not contain business rules — those live in the domain layer.
package usecase

// PlaceOrderUseCase orchestrates the order placement flow.
// It is the single entry point for placing an order in the system.
type PlaceOrderUseCase struct {
    orders    port.OrderRepository   // output port
    products  port.ProductCatalog    // output port (ACL behind this interface)
    publisher port.EventPublisher    // output port
    uow       port.UnitOfWork        // output port
}

// PlaceOrderInput carries the validated command data from the inbound adapter.
type PlaceOrderInput struct {
    CustomerID string
    Items      []OrderItemInput
}

// Execute runs the place-order use case.
// Returns ErrProductNotFound if any item references an unknown product.
// Returns ErrInvalidOrder if the resulting order fails domain invariants.
func (uc *PlaceOrderUseCase) Execute(ctx context.Context, in PlaceOrderInput) (PlaceOrderOutput, error) {
    // 1. Load referenced products via output port
    // 2. Build domain aggregate
    // 3. Call domain method (enforce invariants)
    // 4. Persist via output port
    // 5. Publish domain events
    // 6. Return output DTO
}
```

**Application layer rules:**
- One struct per use case; each has an `Execute(ctx, Input) (Output, error)` method
- Use case may coordinate multiple repositories but calls ONE aggregate per transaction
- Never returns domain objects — convert to Output DTOs before returning
- Transaction boundary is the use case; inject `UnitOfWork` if multi-repo writes needed

---

## Adapter Layer (In)

```go
// Package http provides the HTTP inbound adapter for the Orders service.
// Handlers translate HTTP requests to use case input DTOs and map output to HTTP responses.
// No business logic belongs here.
package http

// OrderHandler handles HTTP requests for the Orders resource.
type OrderHandler struct {
    placeOrder port.PlaceOrderUseCase // input port interface
}

// PlaceOrder handles POST /orders.
//
// @Summary     Place a new order
// @Tags        orders
// @Accept      json
// @Produce     json
// @Param       body  body     PlaceOrderRequest  true  "Order payload"
// @Success     201   {object} PlaceOrderResponse
// @Failure     400   {object} ErrorResponse
// @Failure     500   {object} ErrorResponse
// @Router      /orders [post]
func (h *OrderHandler) PlaceOrder(w http.ResponseWriter, r *http.Request) {
    var req PlaceOrderRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        writeError(w, http.StatusBadRequest, "invalid_request", err.Error())
        return
    }
    if err := validate(req); err != nil {
        writeError(w, http.StatusBadRequest, "validation_error", err.Error())
        return
    }
    out, err := h.placeOrder.Execute(r.Context(), req.toInput())
    if err != nil {
        mapDomainError(w, err)
        return
    }
    writeJSON(w, http.StatusCreated, PlaceOrderResponse{}.fromOutput(out))
}
```

---

## Adapter Layer (Out) — Persistence

```go
// Package persistence provides DynamoDB implementations of domain repository interfaces.
package persistence

// DynamoOrderRepository implements domain/repository.OrderRepository using AWS DynamoDB.
// All DynamoDB-specific types are confined to this package; domain types are never exposed externally.
type DynamoOrderRepository struct {
    client    *dynamodb.Client
    tableName string
    tracer    trace.Tracer
}

// FindByID retrieves an Order aggregate by its ID from DynamoDB.
// Returns domain.ErrNotFound if the item does not exist.
func (r *DynamoOrderRepository) FindByID(ctx context.Context, id domain.OrderID) (*domain.Order, error) {
    ctx, span := r.tracer.Start(ctx, "DynamoOrderRepository.FindByID")
    defer span.End()

    out, err := r.client.GetItem(ctx, &dynamodb.GetItemInput{
        TableName: &r.tableName,
        Key:       buildKey(id),
    })
    if err != nil { return nil, mapAWSError(err) }
    if out.Item == nil { return nil, domain.ErrNotFound{ID: id.String()} }

    return unmarshalOrder(out.Item)  // converts DynamoDB types to domain aggregate
}
```

---

## Dependency Injection (Wire / Manual)

```go
// main.go — composition root; all wiring happens here, nowhere else.
func main() {
    cfg := configs.Load()

    // Infrastructure
    dynamo    := persistence.NewDynamoClient(cfg.AWS)
    snsClient := messaging.NewSNSPublisher(cfg.AWS)

    // Repositories (out adapters implementing domain ports)
    orderRepo := persistence.NewDynamoOrderRepository(dynamo, cfg.OrdersTable)
    eventPub  := messaging.NewSNSEventPublisher(snsClient, cfg.EventsTopic)

    // Use cases (depend only on interfaces)
    placeOrder := usecase.NewPlaceOrderUseCase(orderRepo, eventPub)

    // HTTP handlers (in adapters)
    handler := httpadapter.NewOrderHandler(placeOrder)

    // Router
    r := chi.NewRouter()
    r.Post("/orders", handler.PlaceOrder)
    http.ListenAndServe(cfg.Addr, r)
}
```

---

## Boundary Enforcement Checklist

Before committing any Go code, verify:

- [ ] `internal/domain` has zero imports outside stdlib and `pkg/`
- [ ] `internal/application` imports only `domain` and `pkg/` — never adapter packages
- [ ] `internal/adapter/in` imports only application ports (`port/input`) — never use case structs directly
- [ ] `internal/adapter/out` imports only domain repository interfaces — never calls use cases
- [ ] `cmd/` (main) is the only place where all layers are imported together
- [ ] Every interface is defined in the **consuming** layer (ports), not the implementing layer
- [ ] No `interface{}` / `any` crossing layer boundaries — use typed DTOs
- [ ] Domain errors are mapped to HTTP / gRPC / event error codes only in adapter/in packages

---

## Go Module Structure

```
module github.com/org/service-name

go 1.23

require (
    github.com/aws/aws-sdk-go-v2           v1.x
    github.com/aws/aws-sdk-go-v2/service/dynamodb
    github.com/aws/aws-sdk-go-v2/service/sns
    go.opentelemetry.io/otel               v1.x
    go.opentelemetry.io/otel/sdk           v1.x
    github.com/go-chi/chi/v5               v5.x
)
```

Keep `go.mod` minimal. Prefer standard library over adding dependencies.
