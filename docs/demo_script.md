# ClaimShield Demo Script

## Goal

Show ingestion, governance, streaming processing, live operational visibility, and optional AI interpretation in one short pass.

## Target Length

60 to 90 seconds

## Script

1. Open Confluent Cloud and show the `claimshield-demo` environment and `claimshield-demo-cluster`.
2. Open the topic list and point out the raw and derived topic families.
3. Open one schema subject in Schema Registry and mention compatibility enforcement.
4. Show one running Flink statement that writes to `claims.risk.alerts` or `providers.risk.scores`.
5. Trigger a new risky claim scenario from a producer.
6. Switch to the dashboard and show the new alert arriving.
7. Open the alert detail and explain the evidence shown in the UI.
8. If copilot is enabled, click the explanation action and show recommended next steps.
9. Finish on Stream Lineage or the connector status page.

## Narration Cues

- "ClaimShield detects claims risk while the workflow is still in motion."
- "Schemas and lineage make the pipeline governed, not just real-time."
- "Flink SQL is the rules engine here, not custom batch code."
- "The dashboard turns stream outputs into an operations view."

## Demo Backup Plan

- Keep one pre-seeded risky scenario available in case live timing drifts.
- Keep one screenshot each for lineage, schema, and dashboard in case the UI is slow.
