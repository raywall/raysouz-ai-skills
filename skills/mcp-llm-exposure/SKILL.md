---
name: mcp-llm-exposure
description: >
  Use this skill when designing or implementing MCP (Model Context Protocol) servers in Go to expose service
  data to LLMs. Triggers include: building MCP servers, exposing tools/resources/prompts via MCP, integrating
  Go services with LLM agents, designing data exposure strategies for AI consumption, or any mention of "MCP",
  "Model Context Protocol", "LLM integration", "AI agent", "tool calling", "resources", "prompts" in the
  context of Go services. Also apply when the user wants to make service data queryable by Claude or other LLMs.
---

# MCP Server Design & LLM Data Exposure in Go

Act as a principal AI integration architect. MCP servers are the data plane for LLM agents — design them with
the same rigour as a public API. Poor MCP design leads to hallucinating agents, insecure data leaks, and
uncontrolled costs. Every design decision here has downstream effects on agent reliability.

---

## MCP Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      LLM Agent (Claude)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ MCP Protocol (JSON-RPC 2.0)
                ┌────────────▼────────────┐
                │     MCP Server (Go)      │
                │  ┌─────────────────────┐ │
                │  │  Tools    (actions) │ │  ← Agent can call
                │  │  Resources (data)   │ │  ← Agent can read
                │  │  Prompts  (templates)│ │  ← Agent can use
                │  └─────────────────────┘ │
                └──────┬──────────┬────────┘
                       │          │
            ┌──────────▼──┐  ┌───▼──────────┐
            │  Domain     │  │  External    │
            │  Services   │  │  Data (DDB,  │
            │  (Use Cases)│  │   RDS, S3)   │
            └─────────────┘  └──────────────┘
```

---

## Phase 1 — MCP Server Scaffold in Go

```go
// Package mcp provides the Model Context Protocol server for the Orders service.
// It exposes domain data and actions as MCP tools, resources, and prompts
// to enable LLM agents to query and interact with the Orders bounded context.
//
// The MCP server is read-heavy and strictly enforces:
//   - Authentication via API key or IAM for every connection
//   - Rate limiting per client to prevent runaway agent costs
//   - Audit logging of every tool invocation
//   - Sanitised output (no PII in tool descriptions or resource URIs)
package mcp

import (
    "context"
    "encoding/json"
    "fmt"
    "log/slog"
    "net/http"
)

// Server is the MCP server for the Orders bounded context.
// It implements the MCP protocol over HTTP+SSE (server-sent events) transport.
type Server struct {
    orderQuery  port.OrderQueryService     // read-only use cases
    productQuery port.ProductQueryService
    rateLimiter RateLimiter
    auth        Authenticator
    logger      *slog.Logger
    tracer      trace.Tracer
}

// MCPRequest is a JSON-RPC 2.0 request from an MCP client (LLM host).
type MCPRequest struct {
    JSONRPC string          `json:"jsonrpc"`
    ID      any             `json:"id"`
    Method  string          `json:"method"`
    Params  json.RawMessage `json:"params"`
}

// MCPResponse is a JSON-RPC 2.0 response to the MCP client.
type MCPResponse struct {
    JSONRPC string `json:"jsonrpc"`
    ID      any    `json:"id"`
    Result  any    `json:"result,omitempty"`
    Error   *MCPError `json:"error,omitempty"`
}
```

---

## Phase 2 — MCP Tools (Agent Actions)

Tools are functions the LLM can invoke. Design them like REST endpoints — explicit inputs, predictable outputs.

### Tool Registration

```go
// Tool describes an MCP tool available to the LLM agent.
// Descriptions must be precise — the LLM uses them to decide when to call the tool.
type Tool struct {
    Name        string          `json:"name"`
    Description string          `json:"description"`
    InputSchema json.RawMessage `json:"inputSchema"` // JSON Schema
}

// RegisteredTools returns all tools exposed by the Orders MCP server.
// Keep tool count minimal; each tool is a cognitive load on the LLM.
func (s *Server) RegisteredTools() []Tool {
    return []Tool{
        {
            Name: "get_order",
            Description: `Retrieve a single order by its unique ID.
Use this tool when the user asks about a specific order status, items, or total.
Do NOT use this tool to list or search orders — use search_orders instead.
Returns: order ID, status, items, totals, timestamps, and shipping info.`,
            InputSchema: mustSchema(GetOrderInput{}),
        },
        {
            Name: "search_orders",
            Description: `Search orders by customer, status, date range, or amount.
Use this when the user wants to find orders matching criteria rather than asking about one specific order.
Results are paginated; use the cursor field to fetch subsequent pages.
Limit: maximum 50 orders per call.`,
            InputSchema: mustSchema(SearchOrdersInput{}),
        },
        {
            Name: "get_order_metrics",
            Description: `Retrieve aggregated order metrics for a time range.
Returns: order volume, GMV, average order value, top products, cancellation rate.
Use this for business intelligence questions, trend analysis, and dashboards.`,
            InputSchema: mustSchema(GetOrderMetricsInput{}),
        },
    }
}
```

### Tool Handler

```go
// GetOrderInput defines the input schema for the get_order tool.
type GetOrderInput struct {
    // OrderID is the unique identifier of the order to retrieve.
    // Format: "ord_" followed by a 26-character ULID string.
    OrderID string `json:"order_id" jsonschema:"required,pattern=^ord_[0-9A-Z]{26}$"`
}

// handleGetOrder processes the get_order tool invocation.
// It enforces input validation, rate limiting, and audit logging before calling the domain service.
func (s *Server) handleGetOrder(ctx context.Context, raw json.RawMessage) (any, error) {
    ctx, span := s.tracer.Start(ctx, "MCPServer.handleGetOrder")
    defer span.End()

    var input GetOrderInput
    if err := json.Unmarshal(raw, &input); err != nil {
        return nil, &MCPError{Code: -32602, Message: "invalid params: " + err.Error()}
    }
    if err := validate(input); err != nil {
        return nil, &MCPError{Code: -32602, Message: err.Error()}
    }

    s.logger.InfoContext(ctx, "mcp tool invoked",
        slog.String("tool", "get_order"),
        slog.String("orderId", input.OrderID),
    )

    order, err := s.orderQuery.GetByID(ctx, input.OrderID)
    if err != nil {
        span.RecordError(err)
        return nil, mapDomainError(err)
    }

    return toOrderView(order), nil  // always return a view DTO, never the domain aggregate
}
```

---

## Phase 3 — MCP Resources (Data URIs)

Resources expose structured data the LLM can read without function-calling overhead.

```go
// ResourceTemplate defines URI templates for MCP resources.
// Resources are read-only; mutations must use tools.
func (s *Server) RegisteredResources() []ResourceTemplate {
    return []ResourceTemplate{
        {
            URITemplate: "orders://order/{order_id}",
            Name:        "Order Detail",
            Description: "Full detail of a single order including line items and status history.",
            MIMEType:    "application/json",
        },
        {
            URITemplate: "orders://customer/{customer_id}/orders",
            Name:        "Customer Orders",
            Description: "Paginated list of all orders for a customer, newest first.",
            MIMEType:    "application/json",
        },
        {
            URITemplate: "orders://metrics/daily/{date}",  // date: YYYY-MM-DD
            Name:        "Daily Order Metrics",
            Description: "Aggregated order metrics for a single day: volume, GMV, AOV, top SKUs.",
            MIMEType:    "application/json",
        },
    }
}

// ReadResource serves a resource request identified by uri.
// URI patterns are matched against RegisteredResources templates.
func (s *Server) ReadResource(ctx context.Context, uri string) (ResourceContent, error) {
    ctx, span := s.tracer.Start(ctx, "MCPServer.ReadResource",
        trace.WithAttributes(attribute.String("mcp.resource.uri", uri)),
    )
    defer span.End()

    route, params, err := s.router.Match(uri)
    if err != nil {
        return ResourceContent{}, &MCPError{Code: -32602, Message: "unknown resource URI"}
    }
    return route.Handler(ctx, params)
}
```

---

## Phase 4 — MCP Prompts (Reusable Templates)

Prompts are pre-built instruction templates the LLM host can inject:

```go
// RegisteredPrompts returns reusable prompt templates for the Orders domain.
// Prompts encode domain expertise so agents don't need to invent queries.
func (s *Server) RegisteredPrompts() []Prompt {
    return []Prompt{
        {
            Name:        "order_investigation",
            Description: "Structured investigation workflow for a customer order issue.",
            Arguments: []PromptArgument{
                {Name: "order_id",  Description: "The order ID to investigate.", Required: true},
                {Name: "issue",     Description: "Brief description of the reported issue.", Required: true},
            },
        },
        {
            Name:        "daily_ops_summary",
            Description: "Generate a daily operations summary for a given date.",
            Arguments: []PromptArgument{
                {Name: "date", Description: "Date in YYYY-MM-DD format.", Required: true},
            },
        },
    }
}

// GetPrompt renders a prompt template with provided arguments.
func (s *Server) GetPrompt(ctx context.Context, name string, args map[string]string) (PromptMessages, error) {
    switch name {
    case "order_investigation":
        return PromptMessages{
            {Role: "user", Content: fmt.Sprintf(
                `Investigate order %s. Reported issue: %s.
                 Steps:
                 1. Retrieve the order details using get_order
                 2. Check the status history and identify any anomalies
                 3. If payment-related, check the payment events
                 4. Summarise findings and suggest resolution`,
                args["order_id"], args["issue"],
            )},
        }, nil
    }
    return nil, fmt.Errorf("unknown prompt: %s", name)
}
```

---

## Phase 5 — Security & Access Control

```go
// MCPAuthMiddleware enforces authentication and authorisation on every MCP request.
// The MCP server is an attack surface — treat every connection as untrusted by default.
type MCPAuthMiddleware struct {
    authenticator Authenticator
    authoriser    Authoriser
    logger        *slog.Logger
}

// Authenticate extracts and validates the bearer token from the Authorization header.
// Supports API key (Bearer sk-...) and AWS IAM SigV4 (used for internal agent invocations).
func (m *MCPAuthMiddleware) Authenticate(ctx context.Context, r *http.Request) (Principal, error) {
    token := r.Header.Get("Authorization")
    if token == "" {
        return Principal{}, ErrUnauthenticated
    }
    return m.authenticator.Verify(ctx, strings.TrimPrefix(token, "Bearer "))
}

// Authorise checks that the principal has permission to invoke the requested tool or resource.
// Tool-level permissions: read-only principals cannot call mutating tools.
// Resource-level permissions: customer data scoped to principal's tenant.
func (m *MCPAuthMiddleware) Authorise(ctx context.Context, p Principal, action string) error {
    if !m.authoriser.Can(p, action) {
        m.logger.WarnContext(ctx, "mcp authorisation denied",
            slog.String("principal", p.ID),
            slog.String("action", action),
        )
        return ErrUnauthorised
    }
    return nil
}
```

### Rate Limiting for Agent Calls

```go
// AgentRateLimiter prevents runaway LLM agents from exhausting service capacity.
// Per-client limits are enforced; bursts are allowed up to the burst factor.
type AgentRateLimiter struct {
    clients sync.Map  // map[clientID]*rate.Limiter
    rps     float64   // sustained rate (requests per second)
    burst   int       // burst capacity
}

// Allow returns true if the client may make a request, false if rate-limited.
// Logs rate limit events for FinOps cost attribution.
func (r *AgentRateLimiter) Allow(ctx context.Context, clientID string) bool {
    limiter, _ := r.clients.LoadOrStore(clientID, rate.NewLimiter(rate.Limit(r.rps), r.burst))
    allowed := limiter.(*rate.Limiter).Allow()
    if !allowed {
        slog.WarnContext(ctx, "mcp rate limit exceeded", slog.String("client", clientID))
    }
    return allowed
}
```

---

## Phase 6 — LLM-Friendly Output Design

Tools must return output that helps the LLM reason correctly:

```go
// OrderView is the MCP output type for an Order.
// Fields are named and documented for LLM comprehension — verbose is better than terse.
// NEVER include raw database IDs, internal flags, or implementation details.
type OrderView struct {
    // OrderID is the unique identifier for this order. Format: "ord_<ULID>"
    OrderID string `json:"order_id"`

    // Status is the current lifecycle state. One of:
    // "draft", "placed", "confirmed", "shipped", "delivered", "cancelled"
    Status string `json:"status"`

    // StatusDescription is a human-readable explanation of what the current status means.
    // Example: "The order has been submitted and is awaiting confirmation."
    StatusDescription string `json:"status_description"`

    // PlacedAt is when the customer submitted the order. ISO 8601 UTC.
    PlacedAt string `json:"placed_at,omitempty"`

    // Items is the list of products in this order.
    Items []OrderItemView `json:"items"`

    // TotalAmountUSD is the order total in US dollars, as a decimal string.
    // Example: "129.99"
    TotalAmountUSD string `json:"total_amount_usd"`

    // CanBeCancelled indicates whether the LLM agent may offer a cancellation action.
    // True only for orders in "placed" status.
    CanBeCancelled bool `json:"can_be_cancelled"`
}
```

---

## MCP Server Checklist

- [ ] Every tool has a precise description explaining WHEN to use it and when NOT to
- [ ] Tool input schemas use JSON Schema with `required` and format constraints
- [ ] Tool handlers validate input before calling domain services
- [ ] Resources have clean URI templates with documented path parameters
- [ ] Prompts encode domain-specific reasoning workflows
- [ ] Authentication enforced on every connection (API key or IAM)
- [ ] Tool-level authorisation prevents unpermitted mutations
- [ ] Per-client rate limiting prevents runaway agent cost
- [ ] Audit log written for every tool invocation (tool name, principal, timestamp)
- [ ] Output DTOs use verbose, self-documenting field names
- [ ] PII fields are masked or omitted in LLM-facing outputs
- [ ] OTEL tracing spans cover every tool and resource handler
- [ ] FinOps tags applied to MCP server compute resources
- [ ] DLQ or error channel for failed async tool invocations
