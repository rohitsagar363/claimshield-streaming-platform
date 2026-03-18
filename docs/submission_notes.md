# ClaimShield Submission Notes

## Required Evidence

- Confluent environment view
- Kafka cluster view
- Topic list
- One raw event schema
- One alert schema
- One running Flink statement
- Stream Lineage view
- Stream Catalog / Data Portal view
- Dashboard with live alerts

## Optional Evidence

- Managed connector configuration and status
- ClaimShield Copilot explanation panel
- Producer terminal showing emitted events

## Reviewer Talking Points

- The project uses Confluent-native building blocks end to end.
- Governance is part of the architecture, not an afterthought.
- Flink SQL owns the core risk rules.
- The dashboard translates streaming outputs into operational action.
- The AI copilot is downstream and explainable, not the source of truth.

## Current Environment Details

- Environment ID: `env-xknzkk`
- Kafka cluster ID: `lkc-v33kk5`
- Schema Registry cluster ID: `lsrc-x11kkk`
- Flink compute pool ID: `lfcp-wnnk39`
- Region: Azure `eastus`
