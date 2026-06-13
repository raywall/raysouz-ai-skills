# Go GraphQL Connector Generation Contract

Use the examples under:

```text
/Users/raysouz/Workspace/estudos/workflows/go-graphql-connector/examples
```

`service.json` references schema/connectors/mock through supported sources and
defines route, formatting, partial-response, features, and authorization.

`schema.json` defines `types` plus a `query` whose root field normally returns a
data-source aggregation object. Supported common kinds are `String`, `Int`,
`Float`, `Boolean`, `Object`, and `List`.

Each `connectors.json` entry maps one aggregation field to an adapter and
defines adapter configuration, response transform, timeout, retries, and
optional resilience.

`connector.go` loads config, creates cloud contexts, builds GraphQL, wraps the
HTTP handler for the selected runtime, exposes `/health`, and starts local or
cloud execution.
