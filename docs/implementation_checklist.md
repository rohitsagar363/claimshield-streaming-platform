# ClaimShield Implementation Checklist

## Foundation

- [x] Confirm Confluent Cloud access
- [x] Use environment `claimshield-demo`
- [x] Confirm Stream Governance is enabled
- [x] Reuse Kafka cluster `claimshield-demo-cluster`
- [x] Create Flink compute pool `claimshield-risk-workspace`
- [x] Create local repository scaffold

## Contracts and Topics

- [x] Write JSON Schema files in `schemas/`
- [x] Register schemas in Schema Registry
- [x] Create raw Kafka topics
- [ ] Verify topic visibility in Stream Catalog

## Producers

- [x] Build `producers/generate_claims.py`
- [x] Build `producers/generate_documents.py`
- [x] Build `producers/generate_status_updates.py`
- [x] Build `producers/generate_provider_profiles.py`
- [x] Add realistic scenario controls for healthy and risky claims
- [x] Smoke test producers against Confluent Cloud

## Flink

- [x] Configure inferred raw Flink tables for JSON Schema subjects
- [x] Build first enrichment preview view layer
- [x] Build curated enrichment statement
- [x] Implement missing documentation rule
- [x] Implement SLA breach rule
- [x] Implement provider risk score rule
- [x] Verify continuous statements are running

## Connector

- [x] Choose HTTP Sink V2 or PostgreSQL Sink
- [x] Create managed connector
- [x] Verify connector delivery or sink writes

## Dashboard

- [x] Build `app/dashboard.py`
- [x] Display KPI cards
- [x] Display live alert feed
- [x] Display provider leaderboard
- [x] Display claim detail table

## Copilot

- [x] Add alert explanation workflow
- [x] Add contextual prompt construction
- [x] Add response panel in dashboard

## Evidence and Submission

- [ ] Capture cluster and environment screenshots
- [ ] Capture schema screenshots
- [ ] Capture running Flink statement screenshot
- [ ] Capture lineage and catalog screenshots
- [ ] Capture dashboard screenshot
- [ ] Capture connector screenshot if used
- [ ] Finalize README
- [ ] Rehearse 60 to 90 second demo
