ALTER TABLE `claims.submitted.raw` SET (
  'value.format' = 'json-registry',
  'value.json-registry.subject-names' = 'claim.submitted.v1'
);

ALTER TABLE `claims.documents.raw` SET (
  'value.format' = 'json-registry',
  'value.json-registry.subject-names' = 'claim.document_uploaded.v1'
);

ALTER TABLE `claims.status.raw` SET (
  'value.format' = 'json-registry',
  'value.json-registry.subject-names' = 'claim.status_updated.v1'
);

ALTER TABLE `providers.profile.raw` SET (
  'value.format' = 'json-registry',
  'value.json-registry.subject-names' = 'provider.profile_updated.v1'
);

ALTER TABLE `claims.payments.raw` SET (
  'value.format' = 'json-registry',
  'value.json-registry.subject-names' = 'claim.payment_processed.v1'
);
