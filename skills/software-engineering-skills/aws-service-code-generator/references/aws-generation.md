# AWS Generation Guide

| Need | Default |
|---|---|
| synchronous public API | API Gateway + Lambda, or ALB + ECS for steady load |
| async command/event | EventBridge or SNS -> SQS -> Lambda |
| owned key-value state | DynamoDB |
| relational invariants/reporting | Aurora/RDS, only with justification |
| object/document storage | S3 |
| secrets | Secrets Manager or SSM SecureString |
| tracing/logs/metrics | OpenTelemetry plus CloudWatch/X-Ray |

Generate least-privilege IAM, encryption, alarms, cost tags, correlation IDs,
structured logs, health checks where applicable, and explicit failure handling.
