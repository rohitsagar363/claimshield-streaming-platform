# Flink SQL Assets

## Execution Order

1. Run `01_configure_inferred_tables.sql` to attach the RecordNameStrategy JSON Schema subjects to the inferred raw topic tables.
2. Run `02_create_enrichment_views.sql` to flatten the raw topic tables and create the first enrichment layer.

## Notes

- The raw Kafka topics were inferred as binary tables because the producers use Schema Registry with RecordNameStrategy.
- The `ALTER TABLE ... SET` statements are required so Flink can resolve the JSON Schema subjects and expose typed columns.
- The enrichment layer is currently modeled as views first. This keeps Step 5 lightweight and verifiable before introducing long-running sink statements for the derived topics.
