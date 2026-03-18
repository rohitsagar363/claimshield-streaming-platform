CREATE VIEW first_claim_documents_v AS
SELECT
  claim_id,
  MIN(uploaded_at) AS first_uploaded_at,
  COUNT(*) AS document_count
FROM claim_documents_v
GROUP BY claim_id;

INSERT INTO `claims.enriched.curated`
SELECT
  claim_id AS `key`,
  claim_id,
  member_id,
  provider_id,
  submitted_at,
  amount,
  procedure_code,
  priority,
  claim_region,
  provider_specialty,
  provider_region,
  provider_risk_tier,
  provider_profile_event_time,
  current_status,
  current_status_reason,
  current_status_event_time
FROM claims_enriched_v;

INSERT INTO `claims.risk.alerts`
SELECT
  CONCAT('ALT-MISSING-DOC-', c.claim_id) AS `key`,
  CONCAT('ALT-MISSING-DOC-', c.claim_id) AS alert_id,
  c.claim_id,
  c.provider_id,
  'missing_documentation' AS alert_type,
  CASE
    WHEN c.priority = 'high' THEN 'critical'
    ELSE 'high'
  END AS severity,
  CONCAT('No supporting document received for claim ', c.claim_id, ' while claim remains open') AS message,
  COALESCE(c.current_status_event_time, c.submitted_at) AS event_time,
  c.current_status,
  c.submitted_at,
  c.priority
FROM claims_enriched_v AS c
LEFT JOIN first_claim_documents_v AS d
  ON c.claim_id = d.claim_id
WHERE d.claim_id IS NULL
  AND c.current_status IN ('submitted', 'pending_review');

INSERT INTO `claims.sla.breaches`
SELECT
  CONCAT('BRCH-SLA-', c.claim_id) AS `key`,
  CONCAT('BRCH-SLA-', c.claim_id) AS breach_id,
  c.claim_id,
  c.provider_id,
  'claim_processing_sla' AS breach_type,
  CASE
    WHEN c.priority = 'high' THEN 'critical'
    ELSE 'high'
  END AS severity,
  CONCAT(
    'Claim ',
    c.claim_id,
    ' has remained in ',
    c.current_status,
    ' beyond the SLA review threshold'
  ) AS message,
  c.submitted_at,
  c.current_status,
  COALESCE(c.current_status_event_time, c.submitted_at) AS event_time
FROM claims_enriched_v AS c
WHERE c.current_status IN ('submitted', 'pending_review')
  AND c.priority IN ('medium', 'high');

INSERT INTO `providers.risk.scores`
SELECT
  provider_id AS `key`,
  provider_id,
  provider_region,
  provider_specialty,
  provider_risk_tier,
  total_claims,
  denied_claims,
  stale_claims,
  missing_document_claims,
  risk_score,
  CASE
    WHEN risk_score >= 80 THEN 'critical'
    WHEN risk_score >= 55 THEN 'high'
    WHEN risk_score >= 30 THEN 'medium'
    ELSE 'low'
  END AS risk_level,
  60 AS score_window_minutes,
  latest_claim_event_time AS event_time
FROM (
  SELECT
    c.provider_id AS provider_id,
    MAX(c.provider_region) AS provider_region,
    MAX(c.provider_specialty) AS provider_specialty,
    MAX(c.provider_risk_tier) AS provider_risk_tier,
    COUNT(*) AS total_claims,
    SUM(CASE WHEN c.current_status = 'denied' THEN 1 ELSE 0 END) AS denied_claims,
    SUM(
      CASE
        WHEN c.current_status IN ('submitted', 'pending_review')
        THEN 1
        ELSE 0
      END
    ) AS stale_claims,
    SUM(
      CASE
        WHEN d.claim_id IS NULL
         AND c.current_status IN ('submitted', 'pending_review', 'denied')
        THEN 1
        ELSE 0
      END
    ) AS missing_document_claims,
    MAX(COALESCE(c.current_status_event_time, c.submitted_at)) AS latest_claim_event_time,
    (
      SUM(CASE WHEN c.current_status = 'denied' THEN 1 ELSE 0 END) * 35.0
      + SUM(
        CASE
          WHEN c.current_status IN ('submitted', 'pending_review')
          THEN 1
          ELSE 0
        END
      ) * 25.0
      + SUM(
        CASE
          WHEN d.claim_id IS NULL
           AND c.current_status IN ('submitted', 'pending_review', 'denied')
          THEN 1
          ELSE 0
        END
      ) * 20.0
    ) / COUNT(*) AS risk_score
  FROM claims_enriched_v AS c
  LEFT JOIN first_claim_documents_v AS d
    ON c.claim_id = d.claim_id
  GROUP BY c.provider_id
);
