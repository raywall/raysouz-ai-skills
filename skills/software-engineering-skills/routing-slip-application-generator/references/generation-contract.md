# Routing Slip Generation Contract

Use the local framework at:

```text
/Users/raysouz/Workspace/estudos/workflows/routing-slip-pattern
```

Workflow headers require name, version, error policy, stable
`message_id_path`, `correlation_id_path`, and ordered steps with stable IDs.

Prefer:

- `validate`, `assert`, `condition`, `cel`, `compute`, `jump_if` for behavior;
- `graphql_enrich` for reads;
- `rest_call` and `aws_action` for effects;
- `audit`, `log`, and metrics for observability;
- `workflow_ref` for composition.

Runtime config must cover trigger, state store, idempotency, processing lock,
metrics, tracing, security redaction, and integration endpoints.
