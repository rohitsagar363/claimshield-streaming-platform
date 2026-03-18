CREATE TABLE `claims.enriched.curated` (
  `key` STRING,
  claim_id STRING,
  member_id STRING,
  provider_id STRING,
  submitted_at STRING,
  amount DOUBLE,
  procedure_code STRING,
  priority STRING,
  claim_region STRING,
  provider_specialty STRING,
  provider_region STRING,
  provider_risk_tier STRING,
  provider_profile_event_time STRING,
  current_status STRING,
  current_status_reason STRING,
  current_status_event_time STRING,
  PRIMARY KEY (`key`) NOT ENFORCED
) WITH (
  'changelog.mode' = 'upsert',
  'kafka.cleanup-policy' = 'delete-compact',
  'key.format' = 'raw',
  'value.fields-include' = 'all',
  'value.format' = 'json-registry'
);

CREATE TABLE `claims.risk.alerts` (
  `key` STRING,
  alert_id STRING,
  claim_id STRING,
  provider_id STRING,
  alert_type STRING,
  severity STRING,
  message STRING,
  event_time STRING,
  current_status STRING,
  submitted_at STRING,
  priority STRING,
  PRIMARY KEY (`key`) NOT ENFORCED
) WITH (
  'changelog.mode' = 'upsert',
  'kafka.cleanup-policy' = 'delete-compact',
  'key.format' = 'raw',
  'value.fields-include' = 'all',
  'value.format' = 'json-registry'
);

CREATE TABLE `claims.sla.breaches` (
  `key` STRING,
  breach_id STRING,
  claim_id STRING,
  provider_id STRING,
  breach_type STRING,
  severity STRING,
  message STRING,
  submitted_at STRING,
  current_status STRING,
  event_time STRING,
  PRIMARY KEY (`key`) NOT ENFORCED
) WITH (
  'changelog.mode' = 'upsert',
  'kafka.cleanup-policy' = 'delete-compact',
  'key.format' = 'raw',
  'value.fields-include' = 'all',
  'value.format' = 'json-registry'
);

CREATE TABLE `providers.risk.scores` (
  `key` STRING,
  provider_id STRING,
  provider_region STRING,
  provider_specialty STRING,
  provider_risk_tier STRING,
  total_claims BIGINT,
  denied_claims BIGINT,
  stale_claims BIGINT,
  missing_document_claims BIGINT,
  risk_score DOUBLE,
  risk_level STRING,
  score_window_minutes INT,
  event_time STRING,
  PRIMARY KEY (`key`) NOT ENFORCED
) WITH (
  'changelog.mode' = 'upsert',
  'kafka.cleanup-policy' = 'delete-compact',
  'key.format' = 'raw',
  'value.fields-include' = 'all',
  'value.format' = 'json-registry'
);
