# Business Rules Script Contract

```yaml
id: "<uuid>"
name: "<use case>"
description: "<scope and source IDs>"
input:
  field:
    type: string
    label: "Field"
    example: "value"
mocks:
  source_name:
    source: "GET /resource/{input.field}"
    data: {}
steps:
  - name: Validate
    condition: "input.field != ''"
    on_fail:
      action: ABORT
      message: "Business rejection"
  - name: Load Context
    use_mock: source_name
    assign: context
  - name: Calculate
    assign: calculated
    compute:
      - name: value
        expr: "1.0"
  - name: Result
    result:
      - name: status
        expr: "'APPROVED'"
```

Supported failure actions: `ABORT`, `SKIP`, and `CONTINUE`. Use CEL for
conditions, calculations, results, and link input mappings.
