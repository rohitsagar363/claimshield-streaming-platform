# ClaimShield PRD

## Product Summary

ClaimShield is a real-time healthcare claims risk intelligence application for detecting claim workflow risk as events happen. The product combines governed event streams, Flink SQL rules, and a live dashboard for claims operations teams.

## Problem Statement

Claims organizations struggle with:

- Missing documentation discovered too late
- Claims stuck in `submitted` or `pending_review`
- Weak visibility into provider-specific delay or denial patterns
- Fragmented tooling between streaming infrastructure and business-facing operations

## Users

- Claims operations analysts
- Claims operations managers
- Provider network risk teams
- Demo judges evaluating streaming architecture and business impact

## MVP Goals

- Ingest realistic claims workflow events into Confluent Cloud
- Govern events with Schema Registry and Stream Governance
- Use Flink SQL as the primary rules engine
- Publish live claim alerts and provider risk scores to Kafka
- Show outcomes in a Streamlit dashboard
- Optionally explain alerts with ClaimShield Copilot

## Non-Goals

- Full claims adjudication
- Bidirectional claims workflow management
- Production-grade PHI handling
- Full EHR or payer system integration

## MVP Functional Requirements

### Ingestion

- Produce claim submission, document upload, status update, provider profile, and payment events
- Use JSON Schema contracts for raw and alert events
- Include enough variance to demonstrate on-time, delayed, and high-risk cases

### Stream Processing

- Join claims with provider context and latest status
- Detect missing documentation within SLA windows
- Detect claims breaching time thresholds in risky statuses
- Compute rolling provider risk scores

### Dashboard

- Show live alert feed
- Highlight active claims and high-risk claims
- Display SLA breaches and flagged providers
- Support drill-down into claim and provider context

### Copilot

- Explain why an alert fired
- Cite the event evidence used
- Suggest next action and urgency

## Success Criteria

- A newly produced claim can trigger a governed Flink rule and appear live in the dashboard
- Governance artifacts are visible in Confluent Cloud
- Lineage clearly shows raw-to-derived topic flow
- The demo can be completed in 60 to 90 seconds

## Risks

- Connector setup could take longer than the core streaming path
- Flink SQL rule tuning may need iteration for believable demo timing
- Dashboard polling latency can reduce demo impact if refresh logic is weak

## Open Decisions

- Whether the connector is HTTP Sink V2 or PostgreSQL Sink
- Whether Copilot uses OpenAI directly or a proxy layer
