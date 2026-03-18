CREATE VIEW claims_submitted_v AS
SELECT
  CAST(`key` AS STRING) AS kafka_key,
  `claim.submitted.v1`.claim_id AS claim_id,
  `claim.submitted.v1`.member_id AS member_id,
  `claim.submitted.v1`.provider_id AS provider_id,
  `claim.submitted.v1`.submitted_at AS submitted_at,
  `claim.submitted.v1`.amount AS amount,
  `claim.submitted.v1`.procedure_code AS procedure_code,
  `claim.submitted.v1`.priority AS priority,
  `claim.submitted.v1`.region AS claim_region
FROM `claims.submitted.raw`
WHERE `claim.submitted.v1` IS NOT NULL;

CREATE VIEW claim_documents_v AS
SELECT
  CAST(`key` AS STRING) AS kafka_key,
  `claim.document_uploaded.v1`.document_id AS document_id,
  `claim.document_uploaded.v1`.claim_id AS claim_id,
  `claim.document_uploaded.v1`.document_type AS document_type,
  `claim.document_uploaded.v1`.uploaded_at AS uploaded_at,
  `claim.document_uploaded.v1`.uploaded_by AS uploaded_by
FROM `claims.documents.raw`
WHERE `claim.document_uploaded.v1` IS NOT NULL;

CREATE VIEW claim_status_events_v AS
SELECT
  CAST(`key` AS STRING) AS kafka_key,
  `claim.status_updated.v1`.claim_id AS claim_id,
  `claim.status_updated.v1`.old_status AS old_status,
  `claim.status_updated.v1`.new_status AS new_status,
  `claim.status_updated.v1`.reason AS reason,
  `claim.status_updated.v1`.event_time AS event_time
FROM `claims.status.raw`
WHERE `claim.status_updated.v1` IS NOT NULL;

CREATE VIEW provider_profiles_v AS
SELECT
  CAST(`key` AS STRING) AS kafka_key,
  `provider.profile_updated.v1`.provider_id AS provider_id,
  `provider.profile_updated.v1`.specialty AS specialty,
  `provider.profile_updated.v1`.region AS region,
  `provider.profile_updated.v1`.risk_tier AS risk_tier,
  `provider.profile_updated.v1`.event_time AS event_time
FROM `providers.profile.raw`
WHERE `provider.profile_updated.v1` IS NOT NULL;

CREATE VIEW claim_payments_v AS
SELECT
  CAST(`key` AS STRING) AS kafka_key,
  `claim.payment_processed.v1`.payment_id AS payment_id,
  `claim.payment_processed.v1`.claim_id AS claim_id,
  `claim.payment_processed.v1`.paid_amount AS paid_amount,
  `claim.payment_processed.v1`.paid_at AS paid_at
FROM `claims.payments.raw`
WHERE `claim.payment_processed.v1` IS NOT NULL;

CREATE VIEW latest_claim_status_v AS
SELECT claim_id, new_status, reason, event_time
FROM (
  SELECT
    claim_id,
    new_status,
    reason,
    event_time,
    ROW_NUMBER() OVER (PARTITION BY claim_id ORDER BY event_time DESC) AS row_num
  FROM claim_status_events_v
)
WHERE row_num = 1;

CREATE VIEW latest_provider_profiles_v AS
SELECT provider_id, specialty, region, risk_tier, event_time
FROM (
  SELECT
    provider_id,
    specialty,
    region,
    risk_tier,
    event_time,
    ROW_NUMBER() OVER (PARTITION BY provider_id ORDER BY event_time DESC) AS row_num
  FROM provider_profiles_v
)
WHERE row_num = 1;

CREATE VIEW claims_enriched_v AS
SELECT
  c.claim_id,
  c.member_id,
  c.provider_id,
  c.submitted_at,
  c.amount,
  c.procedure_code,
  c.priority,
  c.claim_region,
  p.specialty AS provider_specialty,
  p.region AS provider_region,
  p.risk_tier AS provider_risk_tier,
  p.event_time AS provider_profile_event_time,
  COALESCE(s.new_status, 'submitted') AS current_status,
  s.reason AS current_status_reason,
  s.event_time AS current_status_event_time
FROM claims_submitted_v AS c
LEFT JOIN latest_provider_profiles_v AS p
  ON c.provider_id = p.provider_id
LEFT JOIN latest_claim_status_v AS s
  ON c.claim_id = s.claim_id;
