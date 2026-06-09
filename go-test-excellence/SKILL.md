---
name: go-testing-excellence
description: >
  Use this skill whenever writing or reviewing tests for Go code. Triggers include: unit tests,
  integration tests, table-driven tests, subtests, mocks, fakes, stubs, HTTP handler tests,
  database tests, benchmark functions, fuzz tests, test helpers, test fixtures, coverage reports,
  race condition tests, or any mention of "test", "testing", "testify", "mock", "benchmark",
  "fuzz", "TDD", "coverage", "go test", "t.Run", "t.Helper", "httptest", "sqlmock", "golden file"
  in a Go context. Apply before generating any *_test.go file. Also apply when asked to increase
  coverage, refactor tests, or review test quality on existing code.
---

# Go Testing Excellence

Act as a senior Go engineer who treats tests as the primary design tool, not an afterthought.
Tests are executable specifications — they must be readable, deterministic, fast, and honest about
what they verify. A test that always passes regardless of the implementation is worse than no test.

---

## Foundational Rules

1. **Test behaviour, not implementation** — test what a function does, not how it does it
2. **One logical assertion per test case** — multiple `assert` calls are fine; multiple unrelated
   scenarios in one test function are not
3. **Tests must be deterministic** — no `time.Now()`, `rand`, or external network calls in unit tests
4. **Table-driven by default** — use `t.Run` subtests for any function with more than two input variations
5. **Always run with `-race`** — `go test -race ./...` is the minimum bar; never disable the race detector
6. **Test files mirror package structure** — `internal/domain/order.go` → `internal/domain/order_test.go`
7. **Use `_test` package suffix for black-box tests** — `package domain_test` forces testing the public API
8. **`t.Helper()` in every helper function** — ensures failure lines point to the call site, not the helper

---

## Package Conventions

```
internal/
└── domain/
    ├── order.go
    ├── order_test.go          ← white-box: package domain (tests unexported internals if needed)
    └── order_external_test.go ← black-box: package domain_test (tests public API only)

internal/adapter/in/http/
├── order_handler.go
└── order_handler_test.go      ← always black-box for HTTP handlers

testdata/                      ← golden files, fixtures, SQL seeds (never generated — committed)
├── order_placed.golden.json
└── fixtures/
    └── orders.sql
```

---

## Pattern 1 — Table-Driven Tests with Subtests

The canonical Go testing pattern. Use for any function with varying inputs, edge cases, or error paths.

```go
// order_test.go
package domain_test

import (
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"

    "github.com/org/service/internal/domain"
)

// TestOrder_Place verifies all state transitions and invariant checks for Order.Place.
// Each case is independent — no shared mutable state between subtests.
func TestOrder_Place(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name        string
        setup       func() *domain.Order    // builder; never shared between cases
        wantErr     bool
        wantErrType error                   // nil = any error; typed = exact match
        wantStatus  domain.OrderStatus
        wantEvents  int                     // number of domain events produced
    }{
        {
            name: "places a valid draft order",
            setup: func() *domain.Order {
                o, _ := domain.NewOrder("cust-1", []domain.OrderItem{
                    {ProductID: "prod-1", Quantity: 2, Price: domain.MustMoney(1000, "USD")},
                })
                return o
            },
            wantErr:    false,
            wantStatus: domain.StatusPlaced,
            wantEvents: 1,
        },
        {
            name: "rejects an already placed order",
            setup: func() *domain.Order {
                o, _ := domain.NewOrder("cust-1", []domain.OrderItem{
                    {ProductID: "prod-1", Quantity: 1, Price: domain.MustMoney(500, "USD")},
                })
                _ = o.Place()
                return o
            },
            wantErr:     true,
            wantErrType: domain.ErrInvalidTransition{},
        },
        {
            name: "rejects an order with no items",
            setup: func() *domain.Order {
                o, _ := domain.NewOrder("cust-1", nil)
                return o
            },
            wantErr:     true,
            wantErrType: domain.ErrEmptyOrder{},
        },
        {
            name: "rejects an order with zero total",
            setup: func() *domain.Order {
                o, _ := domain.NewOrder("cust-1", []domain.OrderItem{
                    {ProductID: "prod-1", Quantity: 1, Price: domain.MustMoney(0, "USD")},
                })
                return o
            },
            wantErr:     true,
            wantErrType: domain.ErrZeroTotal{},
        },
    }

    for _, tc := range tests {
        tc := tc  // capture — required for Go < 1.22
        t.Run(tc.name, func(t *testing.T) {
            t.Parallel()  // subtests parallelise unless they share state

            order := tc.setup()
            err := order.Place()

            if tc.wantErr {
                require.Error(t, err)
                if tc.wantErrType != nil {
                    assert.IsType(t, tc.wantErrType, err)
                }
                return
            }

            require.NoError(t, err)
            assert.Equal(t, tc.wantStatus, order.Status())
            assert.Len(t, order.DomainEvents(), tc.wantEvents)
        })
    }
}
```

---

## Pattern 2 — Test Helpers and Builders

Eliminate repetitive setup with builders and `t.Helper()`. Never use `init()` or package-level vars
that survive between tests.

```go
// testhelpers_test.go  (in the same package as the tests that use it)
package domain_test

import (
    "testing"

    "github.com/org/service/internal/domain"
)

// orderBuilder is a fluent builder for constructing Order test fixtures.
// It never fails silently — any invalid state calls t.Fatal immediately.
type orderBuilder struct {
    t          *testing.T
    customerID string
    items      []domain.OrderItem
    placed     bool
}

// newOrderBuilder returns a builder pre-configured with sensible defaults.
func newOrderBuilder(t *testing.T) *orderBuilder {
    t.Helper()
    return &orderBuilder{
        t:          t,
        customerID: "cust-test-1",
        items: []domain.OrderItem{
            {ProductID: "prod-test-1", Quantity: 1, Price: domain.MustMoney(1000, "USD")},
        },
    }
}

func (b *orderBuilder) withCustomer(id string) *orderBuilder { b.customerID = id; return b }
func (b *orderBuilder) withItems(items ...domain.OrderItem) *orderBuilder { b.items = items; return b }
func (b *orderBuilder) placed() *orderBuilder                             { b.placed = true; return b }

// build constructs the Order and fails the test immediately if construction fails.
func (b *orderBuilder) build() *domain.Order {
    b.t.Helper()
    o, err := domain.NewOrder(b.customerID, b.items)
    if err != nil {
        b.t.Fatalf("orderBuilder.build: %v", err)
    }
    if b.placed {
        if err := o.Place(); err != nil {
            b.t.Fatalf("orderBuilder.build (place): %v", err)
        }
    }
    return o
}

// assertOrderStatus is a test helper that checks order status with a clear failure message.
func assertOrderStatus(t *testing.T, order *domain.Order, want domain.OrderStatus) {
    t.Helper()
    if got := order.Status(); got != want {
        t.Errorf("order status: got %q, want %q", got, want)
    }
}
```

Usage:
```go
func TestOrder_Cancel(t *testing.T) {
    t.Parallel()
    order := newOrderBuilder(t).placed().build()

    err := order.Cancel("customer request")

    require.NoError(t, err)
    assertOrderStatus(t, order, domain.StatusCancelled)
}
```

---

## Pattern 3 — Mocking with Interfaces

Never use concrete types in tests — always mock interfaces. Prefer hand-written fakes for simple
interfaces; use `github.com/stretchr/testify/mock` or `go.uber.org/mock/gomock` for complex ones.

### Hand-Written Fake (preferred for simple interfaces)

```go
// fakes_test.go
package usecase_test

import (
    "context"
    "sync"

    "github.com/org/service/internal/domain"
)

// fakeOrderRepository is an in-memory implementation of domain.OrderRepository for tests.
// It is safe for concurrent use within a single test.
type fakeOrderRepository struct {
    mu     sync.RWMutex
    orders map[string]*domain.Order
    saveErr error  // inject error to simulate storage failure
}

func newFakeOrderRepository() *fakeOrderRepository {
    return &fakeOrderRepository{orders: make(map[string]*domain.Order)}
}

// withSaveError configures the fake to return err on the next Save call.
func (r *fakeOrderRepository) withSaveError(err error) *fakeOrderRepository {
    r.saveErr = err
    return r
}

func (r *fakeOrderRepository) FindByID(_ context.Context, id domain.OrderID) (*domain.Order, error) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    o, ok := r.orders[id.String()]
    if !ok {
        return nil, domain.ErrNotFound{ID: id.String()}
    }
    return o, nil
}

func (r *fakeOrderRepository) Save(_ context.Context, o *domain.Order) error {
    if r.saveErr != nil {
        err := r.saveErr
        r.saveErr = nil  // consume — one error per call
        return err
    }
    r.mu.Lock()
    defer r.mu.Unlock()
    r.orders[o.ID().String()] = o
    return nil
}

func (r *fakeOrderRepository) NextIdentity() domain.OrderID {
    return domain.NewOrderID()
}
```

### testify/mock (for verifying call expectations)

```go
// mock_event_publisher_test.go
package usecase_test

import (
    "context"

    "github.com/stretchr/testify/mock"

    "github.com/org/service/internal/domain"
)

// MockEventPublisher is a testify mock for port.EventPublisher.
// Use when the test needs to assert that specific events were published.
type MockEventPublisher struct{ mock.Mock }

func (m *MockEventPublisher) Publish(ctx context.Context, event domain.DomainEvent) error {
    args := m.Called(ctx, event)
    return args.Error(0)
}

// Usage in test:
func TestPlaceOrderUseCase_PublishesEvent(t *testing.T) {
    t.Parallel()

    repo      := newFakeOrderRepository()
    publisher := new(MockEventPublisher)

    publisher.On("Publish", mock.Anything, mock.AnythingOfType("domain.OrderPlaced")).
        Return(nil).
        Once()

    uc := usecase.NewPlaceOrderUseCase(repo, publisher)
    _, err := uc.Execute(context.Background(), validPlaceOrderInput())

    require.NoError(t, err)
    publisher.AssertExpectations(t) // fails if Publish was not called exactly once
}
```

---

## Pattern 4 — HTTP Handler Tests

Always use `net/http/httptest`. Never start a real server in unit tests.

```go
// order_handler_test.go
package http_test

import (
    "bytes"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"

    httpadapter "github.com/org/service/internal/adapter/in/http"
)

func TestOrderHandler_PlaceOrder(t *testing.T) {
    t.Parallel()

    tests := []struct {
        name           string
        body           any
        mockUseCase    func() *mockPlaceOrderUseCase
        wantStatusCode int
        wantBody       func(t *testing.T, body []byte)
    }{
        {
            name: "201 on valid request",
            body: map[string]any{
                "customer_id": "cust-1",
                "items": []map[string]any{
                    {"product_id": "prod-1", "quantity": 2},
                },
            },
            mockUseCase: func() *mockPlaceOrderUseCase {
                m := new(mockPlaceOrderUseCase)
                m.On("Execute", mock.Anything, mock.Anything).
                    Return(validPlaceOrderOutput(), nil)
                return m
            },
            wantStatusCode: http.StatusCreated,
            wantBody: func(t *testing.T, body []byte) {
                t.Helper()
                var resp map[string]any
                require.NoError(t, json.Unmarshal(body, &resp))
                assert.NotEmpty(t, resp["order_id"])
            },
        },
        {
            name:        "400 on missing customer_id",
            body:        map[string]any{"items": []any{}},
            mockUseCase: func() *mockPlaceOrderUseCase { return new(mockPlaceOrderUseCase) },
            wantStatusCode: http.StatusBadRequest,
        },
        {
            name: "400 on malformed JSON",
            body: "not-json",
            mockUseCase: func() *mockPlaceOrderUseCase { return new(mockPlaceOrderUseCase) },
            wantStatusCode: http.StatusBadRequest,
        },
    }

    for _, tc := range tests {
        tc := tc
        t.Run(tc.name, func(t *testing.T) {
            t.Parallel()

            uc      := tc.mockUseCase()
            handler := httpadapter.NewOrderHandler(uc)

            bodyBytes, _ := json.Marshal(tc.body)
            req := httptest.NewRequest(http.MethodPost, "/orders", bytes.NewReader(bodyBytes))
            req.Header.Set("Content-Type", "application/json")
            rec := httptest.NewRecorder()

            handler.PlaceOrder(rec, req)

            assert.Equal(t, tc.wantStatusCode, rec.Code)
            if tc.wantBody != nil {
                tc.wantBody(t, rec.Body.Bytes())
            }
            uc.AssertExpectations(t)
        })
    }
}
```

---

## Pattern 5 — Time-Dependent Logic

Never call `time.Now()` directly in domain or application code — inject a clock interface.

```go
// clock.go — in pkg/ or internal/domain
type Clock interface {
    Now() time.Time
}

// RealClock uses the system clock. Inject in production.
type RealClock struct{}
func (RealClock) Now() time.Time { return time.Now() }

// FixedClock returns a fixed time. Inject in tests.
type FixedClock struct{ T time.Time }
func (c FixedClock) Now() time.Time { return c.T }
```

```go
// test using FixedClock
func TestOrder_PlacedAtRecorded(t *testing.T) {
    t.Parallel()

    fixedTime := time.Date(2024, 6, 1, 12, 0, 0, 0, time.UTC)
    clock     := domain.FixedClock{T: fixedTime}
    order     := domain.NewOrderWithClock("cust-1", items, clock)

    _ = order.Place()

    assert.Equal(t, fixedTime, order.PlacedAt())
}
```

---

## Pattern 6 — Database Integration Tests

Use build tags to separate integration tests from unit tests. Use real transactions for isolation —
never clean up with `DELETE FROM` (leaves gaps in auto-increment IDs, causes flaky tests).

```go
//go:build integration
// +build integration

// order_repository_test.go
package persistence_test

import (
    "context"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"

    "github.com/org/service/internal/adapter/out/persistence"
    "github.com/org/service/internal/domain"
)

// TestDynamoOrderRepository_FindByID is an integration test that requires
// a real DynamoDB Local instance. Run with: go test -tags=integration ./...
func TestDynamoOrderRepository_FindByID(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test in short mode")
    }

    ctx   := context.Background()
    db    := setupDynamoLocalForTest(t)  // creates table + registers t.Cleanup to delete it
    repo  := persistence.NewDynamoOrderRepository(db, "test-orders-"+t.Name())

    // Arrange
    order := newOrderBuilder(t).placed().build()
    require.NoError(t, repo.Save(ctx, order))

    // Act
    got, err := repo.FindByID(ctx, order.ID())

    // Assert
    require.NoError(t, err)
    assert.Equal(t, order.ID(), got.ID())
    assert.Equal(t, order.Status(), got.Status())
}

// setupDynamoLocalForTest creates an isolated DynamoDB Local table for this test
// and registers t.Cleanup to delete the table after the test completes.
func setupDynamoLocalForTest(t *testing.T) *dynamodb.Client {
    t.Helper()
    client := dynamodb.NewFromConfig(mustLoadLocalConfig(t))
    tableName := "test-orders-" + t.Name()

    _, err := client.CreateTable(context.Background(), &dynamodb.CreateTableInput{
        TableName:   &tableName,
        // ... key schema, billing mode, etc.
    })
    require.NoError(t, err)

    t.Cleanup(func() {
        _, _ = client.DeleteTable(context.Background(), &dynamodb.DeleteTableInput{
            TableName: &tableName,
        })
    })
    return client
}
```

For SQL databases, use transaction rollback for isolation:

```go
// withTx wraps each test in a transaction that is always rolled back,
// guaranteeing isolation without leaving data in the database.
func withTx(t *testing.T, db *sql.DB, fn func(tx *sql.Tx)) {
    t.Helper()
    tx, err := db.Begin()
    require.NoError(t, err)
    t.Cleanup(func() { _ = tx.Rollback() }) // always rollback; never commit in tests
    fn(tx)
}
```

---

## Pattern 7 — Golden Files

Use golden files for complex output (JSON, SQL, large structs) to avoid brittle string comparisons.

```go
// golden.go — test helper
package testutil

import (
    "os"
    "path/filepath"
    "testing"
)

// AssertMatchesGolden compares got against the content of testdata/<name>.golden.
// Set UPDATE_GOLDEN=true to regenerate golden files when output intentionally changes.
func AssertMatchesGolden(t *testing.T, name string, got []byte) {
    t.Helper()
    path := filepath.Join("testdata", name+".golden")

    if os.Getenv("UPDATE_GOLDEN") == "true" {
        require.NoError(t, os.WriteFile(path, got, 0644))
        t.Logf("golden file updated: %s", path)
        return
    }

    want, err := os.ReadFile(path)
    require.NoError(t, err, "golden file not found — run with UPDATE_GOLDEN=true to create it")
    assert.JSONEq(t, string(want), string(got)) // JSONEq ignores key ordering
}
```

```go
// usage
func TestOrderView_MarshalJSON(t *testing.T) {
    t.Parallel()
    order := newOrderBuilder(t).placed().build()
    view  := toOrderView(order)

    got, err := json.MarshalIndent(view, "", "  ")
    require.NoError(t, err)

    testutil.AssertMatchesGolden(t, "order_placed_view", got)
}
```

Regenerate all golden files: `UPDATE_GOLDEN=true go test ./...`

---

## Pattern 8 — Benchmarks

Write benchmarks alongside unit tests. Always use `b.ReportAllocs()` for allocation-sensitive code.

```go
// order_benchmark_test.go
package domain_test

import (
    "testing"

    "github.com/org/service/internal/domain"
)

// BenchmarkOrder_Place measures the throughput of the order placement flow.
// Run with: go test -bench=BenchmarkOrder_Place -benchmem -count=5 ./internal/domain/
func BenchmarkOrder_Place(b *testing.B) {
    b.ReportAllocs()

    items := []domain.OrderItem{
        {ProductID: "prod-1", Quantity: 2, Price: domain.MustMoney(1000, "USD")},
        {ProductID: "prod-2", Quantity: 1, Price: domain.MustMoney(500, "USD")},
    }

    b.ResetTimer()
    for b.N > 0 {
        b.N--
        o, _ := domain.NewOrder("cust-1", items)
        _ = o.Place()
    }
}

// BenchmarkMoney_Add compares allocation behaviour of value vs pointer Money implementations.
func BenchmarkMoney_Add(b *testing.B) {
    b.ReportAllocs()
    m1 := domain.MustMoney(1000, "USD")
    m2 := domain.MustMoney(500, "USD")

    b.Run("add", func(b *testing.B) {
        for b.N > 0 {
            b.N--
            _, _ = m1.Add(m2)
        }
    })
}
```

Benchmark CI gate (compare against baseline with benchstat):
```bash
# Record baseline on main branch
go test -bench=./... -benchmem -count=10 ./... | tee baseline.txt

# On PR branch
go test -bench=./... -benchmem -count=10 ./... | tee pr.txt

# Compare — fail if any benchmark regressed > 10%
benchstat -delta-test=none baseline.txt pr.txt
```

---

## Pattern 9 — Fuzz Tests (Go 1.18+)

Use fuzzing for parsers, decoders, validators, and any function that processes untrusted input.

```go
// order_fuzz_test.go
package domain_test

import (
    "testing"

    "github.com/org/service/internal/domain"
)

// FuzzMoney_Parse finds inputs that cause NewMoney to panic or behave inconsistently.
// Run corpus: go test -fuzz=FuzzMoney_Parse -fuzztime=60s ./internal/domain/
// Reproduce a finding: go test -run=FuzzMoney_Parse/testdata/corpus/<id> ./internal/domain/
func FuzzMoney_Parse(f *testing.F) {
    // Seed corpus — representative and boundary values
    f.Add(int64(0), "USD")
    f.Add(int64(1), "USD")
    f.Add(int64(-1), "USD")
    f.Add(int64(999999999), "USD")
    f.Add(int64(1000), "EUR")
    f.Add(int64(1000), "")        // invalid currency
    f.Add(int64(1000), "TOOLONG") // too long

    f.Fuzz(func(t *testing.T, amount int64, currency string) {
        // The fuzzer checks for panics automatically.
        // We additionally verify invariants that must hold for valid inputs.
        m, err := domain.NewMoney(amount, currency)
        if err != nil {
            return // invalid input rejected — correct behaviour
        }

        // Invariant: amount must round-trip correctly
        if m.Amount() != amount {
            t.Errorf("amount mismatch: got %d, want %d", m.Amount(), amount)
        }

        // Invariant: adding zero must be identity
        zero := domain.MustMoney(0, currency)
        result, err := m.Add(zero)
        if err != nil {
            t.Errorf("unexpected error adding zero: %v", err)
        }
        if result.Amount() != m.Amount() {
            t.Errorf("add zero changed amount: got %d, want %d", result.Amount(), m.Amount())
        }
    })
}
```

Fuzz findings are saved as corpus files in `testdata/fuzz/FuzzFunctionName/` — commit them.

---

## Pattern 10 — Concurrency Tests

Test concurrent behaviour explicitly. Do not rely on the race detector alone for correctness.

```go
// worker_pool_test.go
package concurrency_test

import (
    "context"
    "sync/atomic"
    "testing"

    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

// TestWorkerPool_ProcessesAllItems verifies that all items are processed exactly once,
// even under concurrent execution. Run with -race to detect data races.
func TestWorkerPool_ProcessesAllItems(t *testing.T) {
    t.Parallel()

    const itemCount = 1000
    var processed atomic.Int64

    items := make([]int, itemCount)
    for i := range items { items[i] = i }

    results, err := workerPool(context.Background(), items, 10,
        func(_ context.Context, n int) (int, error) {
            processed.Add(1)
            return n * 2, nil
        },
    )

    require.NoError(t, err)
    assert.Equal(t, int64(itemCount), processed.Load(), "each item must be processed exactly once")
    assert.Len(t, results, itemCount)
}

// TestWorkerPool_RespectsContextCancellation verifies the pool stops on ctx cancellation.
func TestWorkerPool_RespectsContextCancellation(t *testing.T) {
    t.Parallel()

    ctx, cancel := context.WithCancel(context.Background())
    cancel() // cancel immediately

    items := []int{1, 2, 3, 4, 5}
    _, err := workerPool(ctx, items, 2, func(ctx context.Context, n int) (int, error) {
        return n, ctx.Err()
    })

    assert.ErrorIs(t, err, context.Canceled)
}
```

---

## Coverage Configuration

### Minimum thresholds (enforce in CI)

```bash
# CI step — fails if total coverage drops below 80%
go test -coverprofile=coverage.out -covermode=atomic ./...
go tool cover -func=coverage.out | awk '
  /^total:/ {
    gsub(/%/, "", $3)
    if ($3 + 0 < 80) {
      print "Coverage " $3 "% is below 80% threshold"
      exit 1
    }
    print "Coverage: " $3 "%"
  }
'
```

### Exclude generated and wired code from coverage

```
# .coverignore (used by some tools) or filter in CI
./cmd/...            # main packages — not business logic
./internal/wire/...  # generated DI
./testdata/...
./mock*/...
```

### Per-package coverage report (HTML)

```bash
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out -o coverage.html
```

---

## Build Tags Strategy

```go
// Unit tests — no build tag; always run
// go test ./...

// Integration tests — require external services
//go:build integration
// go test -tags=integration ./...

// End-to-end tests — require full stack
//go:build e2e
// go test -tags=e2e ./...

// Slow tests — benchmarks and fuzz seeds
//go:build slow
// go test -tags=slow ./...
```

`Makefile` targets:
```makefile
.PHONY: test test-integration test-bench test-fuzz

test:
	go test -race -count=1 ./...

test-integration:
	go test -race -tags=integration -count=1 ./...

test-bench:
	go test -bench=./... -benchmem -count=5 -run='^$$' ./...

test-fuzz:
	go test -fuzz=. -fuzztime=60s ./internal/domain/...
```

---

## golangci-lint Configuration for Tests

```yaml
# .golangci.yml
linters:
  enable:
    - testifylint     # enforce correct testify usage (assert vs require, argument order)
    - tparallel       # detect missing t.Parallel() calls
    - thelper         # enforce t.Helper() in test helpers
    - noctx           # detect missing context propagation
    - paralleltest    # detect table-driven tests missing t.Parallel() in subtests

linters-settings:
  testifylint:
    enable-all: true
  tparallel:
    ignore-missing: false
```

---

## Testing Quality Checklist

Before committing any `*_test.go` file:

- [ ] Every test function calls `t.Parallel()` unless it modifies global state
- [ ] Every subtest in a table-driven test calls `t.Parallel()` and captures loop variables
- [ ] Every test helper calls `t.Helper()` as its first statement
- [ ] No `time.Sleep` in tests — use channels, `sync` primitives, or `require.Eventually`
- [ ] No `time.Now()` in domain/application code — Clock interface injected
- [ ] No real HTTP calls in unit tests — use `httptest.NewServer` or `httptest.NewRecorder`
- [ ] No `os.Getenv` in domain tests — configuration injected
- [ ] Integration tests guarded by `//go:build integration` tag and `testing.Short()` skip
- [ ] Fuzz seed corpus covers: zero value, boundary values, invalid inputs, unicode
- [ ] Golden files committed to `testdata/` and regeneration documented
- [ ] Benchmarks include `b.ReportAllocs()` for allocation-sensitive code
- [ ] `go test -race ./...` passes with zero races
- [ ] `golangci-lint run ./...` passes (testifylint + tparallel + thelper)
- [ ] Coverage ≥ 80% on `internal/domain/` and `internal/application/`
- [ ] Mock `AssertExpectations(t)` called at end of every test using testify mocks