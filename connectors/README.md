# Connector Plan

## PostgreSQL Sink Choice

This project uses a single managed PostgreSQL sink connector for the `claims.risk.alerts` topic.

Why this topic:

- It is the clearest action-oriented stream for a sink demo.
- One connector is sufficient for the challenge story.
- It avoids unnecessary duplication while still showing managed integration.

## Sink Target

- Kafka topic: `claims.risk.alerts`
- PostgreSQL table: `claims_risk_alerts`
- Connector name: `claimshield-postgres-alerts-sink`
- Connector ID: `lcc-d77p61`

## Connector Mode

- Connector plugin: `PostgresSink`
- Value format: `JSON_SR`
- Key format: `STRING`
- Insert mode: `UPSERT`
- Primary key mode: `record_key`
- Primary key field: `key`
- Delete handling: `delete.enabled=true`

## Runtime Notes

- The Neon PostgreSQL target must be reachable from Confluent Cloud over TLS.
- Because the Flink output topic is an upsert stream, the sink must enable `delete.enabled=true` to handle tombstone records correctly.

## Verification

- Connector state: `RUNNING`
- Table state: `public.claims_risk_alerts` exists in `neondb`
- Verified rows: 2 alert records present after connector startup

## Template

Use `postgres_claims_risk_alerts_sink.template.json` as the reusable starting config for another PostgreSQL target.
