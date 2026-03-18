from __future__ import annotations

from datetime import datetime, timedelta, timezone


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _base_time() -> datetime:
    return datetime.now(timezone.utc)


def _claim_identifiers(batch_number: int) -> list[dict[str, str]]:
    base_claim = 100245 + (batch_number * 10)
    base_member = 8821 + (batch_number * 10)
    return [
        {
            "claim_id": f"CLM{base_claim + 0}",
            "member_id": f"MBR{base_member + 0}",
        },
        {
            "claim_id": f"CLM{base_claim + 1}",
            "member_id": f"MBR{base_member + 1}",
        },
        {
            "claim_id": f"CLM{base_claim + 2}",
            "member_id": f"MBR{base_member + 2}",
        },
        {
            "claim_id": f"CLM{base_claim + 3}",
            "member_id": f"MBR{base_member + 3}",
        },
        {
            "claim_id": f"CLM{base_claim + 4}",
            "member_id": f"MBR{base_member + 4}",
        },
        {
            "claim_id": f"CLM{base_claim + 5}",
            "member_id": f"MBR{base_member + 5}",
        },
    ]


def _document_ids(batch_number: int) -> list[str]:
    base_document = 7781 + (batch_number * 10)
    return [
        f"DOC{base_document + 0}",
        f"DOC{base_document + 1}",
        f"DOC{base_document + 2}",
        f"DOC{base_document + 3}",
    ]


def provider_profiles(batch_number: int = 0) -> list[dict]:
    now = _base_time() + timedelta(seconds=batch_number)
    return [
        {
            "provider_id": "PRV331",
            "specialty": "orthopedics",
            "region": "Northeast",
            "risk_tier": "medium",
            "event_time": _iso(now - timedelta(minutes=60)),
        },
        {
            "provider_id": "PRV552",
            "specialty": "cardiology",
            "region": "Midwest",
            "risk_tier": "low",
            "event_time": _iso(now - timedelta(minutes=58)),
        },
        {
            "provider_id": "PRV784",
            "specialty": "pain_management",
            "region": "South",
            "risk_tier": "high",
            "event_time": _iso(now - timedelta(minutes=55)),
        },
        {
            "provider_id": "PRV998",
            "specialty": "neurology",
            "region": "Northeast",
            "risk_tier": "high",
            "event_time": _iso(now - timedelta(minutes=52)),
        },
    ]


def claim_submissions(batch_number: int = 0) -> list[dict]:
    now = _base_time()
    ids = _claim_identifiers(batch_number)
    return [
        {
            "claim_id": ids[0]["claim_id"],
            "member_id": ids[0]["member_id"],
            "provider_id": "PRV331",
            "submitted_at": _iso(now - timedelta(minutes=35)),
            "amount": 1840.55,
            "procedure_code": "PROC_123",
            "priority": "high",
            "region": "Northeast",
        },
        {
            "claim_id": ids[1]["claim_id"],
            "member_id": ids[1]["member_id"],
            "provider_id": "PRV784",
            "submitted_at": _iso(now - timedelta(minutes=30)),
            "amount": 2285.10,
            "procedure_code": "PROC_201",
            "priority": "high",
            "region": "South",
        },
        {
            "claim_id": ids[2]["claim_id"],
            "member_id": ids[2]["member_id"],
            "provider_id": "PRV784",
            "submitted_at": _iso(now - timedelta(minutes=28)),
            "amount": 1320.80,
            "procedure_code": "PROC_419",
            "priority": "medium",
            "region": "South",
        },
        {
            "claim_id": ids[3]["claim_id"],
            "member_id": ids[3]["member_id"],
            "provider_id": "PRV552",
            "submitted_at": _iso(now - timedelta(minutes=18)),
            "amount": 950.00,
            "procedure_code": "PROC_099",
            "priority": "low",
            "region": "Midwest",
        },
        {
            "claim_id": ids[4]["claim_id"],
            "member_id": ids[4]["member_id"],
            "provider_id": "PRV998",
            "submitted_at": _iso(now - timedelta(minutes=26)),
            "amount": 2765.45,
            "procedure_code": "PROC_555",
            "priority": "high",
            "region": "Northeast",
        },
        {
            "claim_id": ids[5]["claim_id"],
            "member_id": ids[5]["member_id"],
            "provider_id": "PRV998",
            "submitted_at": _iso(now - timedelta(minutes=24)),
            "amount": 1642.25,
            "procedure_code": "PROC_402",
            "priority": "medium",
            "region": "Northeast",
        },
    ]


def document_uploads(batch_number: int = 0) -> list[dict]:
    now = _base_time()
    ids = _claim_identifiers(batch_number)
    document_ids = _document_ids(batch_number)
    return [
        {
            "document_id": document_ids[0],
            "claim_id": ids[0]["claim_id"],
            "document_type": "clinical_notes",
            "uploaded_at": _iso(now - timedelta(minutes=31)),
            "uploaded_by": "provider_portal",
        },
        {
            "document_id": document_ids[1],
            "claim_id": ids[2]["claim_id"],
            "document_type": "clinical_notes",
            "uploaded_at": _iso(now - timedelta(minutes=6)),
            "uploaded_by": "fax_ingest",
        },
        {
            "document_id": document_ids[2],
            "claim_id": ids[3]["claim_id"],
            "document_type": "referral",
            "uploaded_at": _iso(now - timedelta(minutes=15)),
            "uploaded_by": "provider_portal",
        },
        {
            "document_id": document_ids[3],
            "claim_id": ids[5]["claim_id"],
            "document_type": "prior_auth",
            "uploaded_at": _iso(now - timedelta(minutes=4)),
            "uploaded_by": "ops_user",
        },
    ]


def status_updates(batch_number: int = 0) -> list[dict]:
    now = _base_time()
    ids = _claim_identifiers(batch_number)
    return [
        {
            "claim_id": ids[0]["claim_id"],
            "old_status": "submitted",
            "new_status": "pending_review",
            "reason": "clinical_review_started",
            "event_time": _iso(now - timedelta(minutes=29)),
        },
        {
            "claim_id": ids[0]["claim_id"],
            "old_status": "pending_review",
            "new_status": "approved",
            "reason": "documentation_verified",
            "event_time": _iso(now - timedelta(minutes=20)),
        },
        {
            "claim_id": ids[1]["claim_id"],
            "old_status": "submitted",
            "new_status": "pending_review",
            "reason": "awaiting_documents",
            "event_time": _iso(now - timedelta(minutes=24)),
        },
        {
            "claim_id": ids[2]["claim_id"],
            "old_status": "submitted",
            "new_status": "pending_review",
            "reason": "manual_review_required",
            "event_time": _iso(now - timedelta(minutes=22)),
        },
        {
            "claim_id": ids[2]["claim_id"],
            "old_status": "pending_review",
            "new_status": "denied",
            "reason": "late_supporting_documents",
            "event_time": _iso(now - timedelta(minutes=3)),
        },
        {
            "claim_id": ids[3]["claim_id"],
            "old_status": "submitted",
            "new_status": "approved",
            "reason": "auto_adjudicated",
            "event_time": _iso(now - timedelta(minutes=12)),
        },
        {
            "claim_id": ids[4]["claim_id"],
            "old_status": "submitted",
            "new_status": "pending_review",
            "reason": "awaiting_documents",
            "event_time": _iso(now - timedelta(minutes=21)),
        },
        {
            "claim_id": ids[5]["claim_id"],
            "old_status": "submitted",
            "new_status": "pending_review",
            "reason": "manual_review_required",
            "event_time": _iso(now - timedelta(minutes=17)),
        },
        {
            "claim_id": ids[5]["claim_id"],
            "old_status": "pending_review",
            "new_status": "denied",
            "reason": "provider_pattern_escalation",
            "event_time": _iso(now - timedelta(minutes=2)),
        },
    ]
